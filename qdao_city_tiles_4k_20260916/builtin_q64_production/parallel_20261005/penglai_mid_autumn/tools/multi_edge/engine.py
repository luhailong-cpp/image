"""Direction-aware native geometry. No generation, filesystem writes or visual acceptance."""
from pathlib import Path
import importlib.util
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('multi_edge_legacy_assembly', ROOT/'native_assemble.py')
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
Layout = base.Layout
ROLES = {'north':(-1,0), 'south':(1,0), 'west':(0,-1), 'east':(0,1),
         'northwest':(-1,-1), 'northeast':(-1,1), 'southwest':(1,-1), 'southeast':(1,1)}
SIDES = {'north':'top', 'south':'bottom', 'west':'left', 'east':'right'}


def orientation(name):
    if name not in ['NW','NE','SW','SE']:
        raise ValueError('Wavefront must be NW, NE, SW or SE')
    v = 'north' if name[0] == 'N' else 'south'
    h = 'west' if name[1] == 'W' else 'east'
    return v, h, v+h


def order(layout, name):
    v,h,_ = orientation(name)
    rows = range(layout.count) if v == 'north' else range(layout.count-1,-1,-1)
    cols = range(layout.count) if h == 'west' else range(layout.count-1,-1,-1)
    return [(r,c) for r in rows for c in cols]


def seed_neighbors(layout, neighbors):
    n,h,e = layout.tile,layout.halo,layout.extended
    canvas=np.zeros((e,e,3),np.uint8);known=np.zeros((e,e),bool);records=[]
    for role,image in neighbors.items():
        dr,dc=ROLES[role]
        if image.shape != (n,n,3): raise ValueError('Neighbor dimensions: '+role)
        x0,x1=(n-h,n) if dc<0 else ((0,h) if dc>0 else (0,n))
        y0,y1=(n-h,n) if dr<0 else ((0,h) if dr>0 else (0,n))
        x=0 if dc<0 else (h+n if dc>0 else h)
        y=0 if dr<0 else (h+n if dr>0 else h)
        piece=image[y0:y1,x0:x1]
        canvas[y:y+piece.shape[0],x:x+piece.shape[1]]=piece
        known[y:y+piece.shape[0],x:x+piece.shape[1]]=True
        records.append(dict(role=role,sourceCropLTRB=[x0,y0,x1,y1],canvasPasteXY=[x,y],scale=1))
    return canvas,known,records


def owner_mask(known, edges, layout):
    if not edges:return ~known
    yy,xx=np.indices(known.shape);inside=np.ones_like(known)
    for edge in edges:
        inside &= {'left':xx>=layout.halo,'right':xx<layout.patch-layout.halo,
                   'top':yy>=layout.halo,'bottom':yy<layout.patch-layout.halo}[edge]
    return ~known | inside


def active_edges(layout, row, col, name, neighbors):
    v,h,_=orientation(name)
    start_r=0 if v=='north' else layout.count-1
    start_c=0 if h=='west' else layout.count-1
    return ([SIDES[h]] if col!=start_c or h in neighbors else []) + ([SIDES[v]] if row!=start_r or v in neighbors else [])


def context_operations(layout, row, col, name, neighbors):
    """Actual crop coordinates only; physical pRC coordinates never rotate."""
    v,h,corner=orientation(name);n,s,a,p=layout.tile,layout.stride,layout.halo,layout.patch
    start_r=0 if v=='north' else layout.count-1;start_c=0 if h=='west' else layout.count-1
    prev_r=row-1 if v=='north' else row+1;prev_c=col-1 if h=='west' else col+1
    ops=[]
    def add(source,box,xy,role):ops.append(dict(source=source,cropLTRB=list(box),pasteXY=list(xy),role=role,scale=1))
    if col!=start_c:
        add(f'p{row+1}{prev_c+1}',(s,0,p,p) if h=='west' else (0,0,2*a,p),(0,0) if h=='west' else (s,0),'native '+h+' overlap')
    if row!=start_r:
        add(f'p{prev_r+1}{col+1}',(0,s,p,p) if v=='north' else (0,0,p,2*a),(0,0) if v=='north' else (0,s),'native '+v+' overlap')
    if row!=start_r and col!=start_c:
        x0=s if h=='west' else 0;y0=s if v=='north' else 0
        add(f'p{prev_r+1}{prev_c+1}',(x0,y0,x0+2*a,y0+2*a),(0 if h=='west' else s,0 if v=='north' else s),'authoritative native '+corner+' overlap')
    if row==start_r and v in neighbors:
        x0=col*s-a;lo=max(0,x0);hi=min(n,x0+p);sy=n-a if v=='north' else 0
        add(v,(lo,sy,hi,sy+a),(lo-x0,0 if v=='north' else p-a),'actual external '+v)
    if col==start_c and h in neighbors:
        y0=row*s-a;lo=max(0,y0);hi=min(n,y0+p);sx=n-a if h=='west' else 0
        add(h,(sx,lo,sx+a,hi),(0 if h=='west' else p-a,lo-y0),'actual external '+h)
    if row==start_r and col==start_c and corner in neighbors:
        sx=n-a if h=='west' else 0;sy=n-a if v=='north' else 0
        add(corner,(sx,sy,sx+a,sy+a),(0 if h=='west' else p-a,0 if v=='north' else p-a),'true external '+corner)
    return ops


def materialize_context(layout, ops, images):
    pixels=np.zeros((layout.patch,layout.patch,3),np.uint8);known=np.zeros((layout.patch,layout.patch),bool)
    for op in ops:
        x0,y0,x1,y1=op['cropLTRB'];x,y=op['pasteXY'];piece=images[op['source']][y0:y1,x0:x1]
        if piece.shape[:2]!=(y1-y0,x1-x0):raise ValueError('Crop outside real source')
        pixels[y:y+piece.shape[0],x:x+piece.shape[1]]=piece;known[y:y+piece.shape[0],x:x+piece.shape[1]]=True
    return pixels,known


def inward_weight(layout, edges, return_depth=256):
    yy,xx=np.indices((layout.patch,layout.patch));a=layout.halo;p=layout.patch
    distances={'left':xx-a,'right':p-1-a-xx,'top':yy-a,'bottom':p-1-a-yy}
    return base.smoothstep((return_depth-np.minimum.reduce([distances[e] for e in edges]))/(return_depth-32))


def register_native(context, patch, known, owner, edges, layout, **options):
    """Reflect numerical arrays only to reuse NW math; never transform AI inputs."""
    flip_x='right' in edges;flip_y='bottom' in edges
    if {'left','right'}<=set(edges) or {'top','bottom'}<=set(edges):raise ValueError('Opposite support sides require a different closure method')
    def transform(a):
        if flip_y:a=np.flip(a,0)
        if flip_x:a=np.flip(a,1)
        return np.ascontiguousarray(a)
    canonical=['left' if e=='right' else 'top' if e=='bottom' else e for e in edges]
    result,flow,tone,report=base.register_native(transform(context),transform(patch),transform(known),transform(owner),canonical,layout,**options)
    result=transform(result);flow=transform(flow);tone=transform(tone)
    if flip_x:flow[:,:,0]*=-1
    if flip_y:flow[:,:,1]*=-1
    report.update(edges=edges,numericalCanonicalReflection=dict(horizontal=flip_x,vertical=flip_y,AIInputsTransformed=False),flowConvention='physical source native sampled at physical output XY plus stored flow XY',returnDirection={e:('positive' if e in ['left','top'] else 'negative') for e in edges})
    return result,flow,tone,report


def fold(band, vertical=False):
    sheet=Image.new('RGB',(1024,1280))
    for i in range(4):
        piece=band.crop((0,i*1024,320,(i+1)*1024)) if vertical else band.crop((i*1024,0,(i+1)*1024,320))
        if vertical:piece=piece.transpose(Image.Transpose.ROTATE_90)
        sheet.paste(piece,(0,i*320))
    return sheet


def qa_images(final, neighbors, name, return_depth=256):
    """Yield native-scale sheets with explicit sources; no visual pass implied."""
    if final.size!=(4096,4096):raise ValueError('QA requires4096 tile')
    v,h,corner=orientation(name)
    for axis,negative in [('x',h=='east'),('y',v=='south')]:
        for pos in [1024,2048,3072]:
            image,op=base.full_strip(final,axis,pos)
            yield f'internal-{axis}{pos}-full',image,op,['current']
            ret=pos-return_depth if negative else pos+return_depth
            image,op=base.full_strip(final,axis,ret);op.update(sourceCoreBoundary=pos,returnDirection='negative' if negative else 'positive')
            yield f'internal-{axis}{pos}-return-{ "minus" if negative else "plus"}{return_depth}-full',image,op,['current']
    for y in [1024,2048,3072]:
        for x in [1024,2048,3072]:
            box=[x-160,y-160,x+160,y+160]
            yield f'junction-{x}-{y}',final.crop(box),dict(cropLTRB=box),['current']
    boundary={'north':(0,0,4096,320),'south':(0,3776,4096,4096),'west':(0,0,320,4096),'east':(3776,0,4096,4096)}
    for side in ['north','east','south','west']:
        vertical=side in ['west','east']
        if side in neighbors:
            old=neighbors[side];band=Image.new('RGB',(320,4096) if vertical else (4096,320))
            if side=='north':parts=[(old,(0,3936,4096,4096),(0,0)),(final,(0,0,4096,160),(0,160))]
            elif side=='south':parts=[(final,(0,3936,4096,4096),(0,0)),(old,(0,0,4096,160),(0,160))]
            elif side=='west':parts=[(old,(3936,0,4096,4096),(0,0)),(final,(0,0,160,4096),(160,0))]
            else:parts=[(final,(3936,0,4096,4096),(0,0)),(old,(0,0,160,4096),(160,0))]
            for image,box,xy in parts:band.paste(image.crop(box),xy)
            yield side+'-shared-full',fold(band,vertical),dict(side=side,actualSharedEdge=True,oldContext=160,newContext=160,rotationCCW90=vertical),[side,'current']
        else:
            yield side+'-no-neighbor-unverified',fold(final.crop(boundary[side]),vertical),dict(cropLTRB=boundary[side],side=side,noNeighbor=True,seamAccepted=False),['current']
    for side in [v,h]:
        pos=return_depth if side in ['north','west'] else 4096-return_depth
        image,op=base.full_strip(final,'y' if side in ['north','south'] else 'x',pos)
        op.update(side=side,scope='incoming finite registration return')
        yield f'{side}-return-{return_depth}-full',image,op,['current']
    if all(k in neighbors for k in [v,h,corner]):
        gx=0 if h=='west' else 1;gy=0 if v=='north' else 1
        role_by_offset={offset:role for role,offset in ROLES.items()};sheet=Image.new('RGB',(1024,1024));sources=[];crops=[]
        for iy in range(2):
            for ix in range(2):
                dr,dc=gy-1+iy,gx-1+ix;role='current' if (dr,dc)==(0,0) else role_by_offset[(dr,dc)]
                image=final if role=='current' else neighbors[role]
                x0=3584 if ix==0 else 0;y0=3584 if iy==0 else 0;box=[x0,y0,x0+512,y0+512]
                sheet.paste(image.crop(box),(ix*512,iy*512));sources.append(role);crops.append(box)
        yield 'four-tile-'+corner+'-corner',sheet,dict(tileLocalJunctionXY=[gx*4096,gy*4096],sourceCropLTRB=crops,nativeScale=1),sources

"""Bounded native-pixel overlap quilting; sources and previous assembly are read-only."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
TILE=ROOT/'r08_c09'; NATIVE=TILE/'native'; OUT=TILE/'assembly_v2'
P,C,H,S=1254,1024,115,4326
MAX_SHIFT,MAX_TONE,FADE,TRANSITION=4,16,160,6

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,data): Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(path): return {'file':str(path),'sha256':sha(path)}
def image_array(path):
    with Image.open(path) as im: return np.array(im.convert('RGB'))
def smoothstep(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
def gradient(a):
    f=a.astype(np.float32)
    return np.maximum(np.max(np.abs(np.diff(f,axis=0,prepend=f[:1])),axis=2),
                      np.max(np.abs(np.diff(f,axis=1,prepend=f[:,:1])),axis=2))

def material(a):
    f=a.astype(np.int16);r,g,b=f[:,:,0],f[:,:,1],f[:,:,2]
    # Only isolate the strongly different foliage hue. Subdividing neutral
    # paving by brightness would introduce artificial threshold contours.
    labels=np.ones(a.shape[:2],np.uint8)
    labels[(g>r+5)&(g>b+8)]=0
    return labels

def overlap(a,pa,b,pb):
    ax,ay=pa;bx,by=pb
    x0,y0=max(ax,bx),max(ay,by);x1,y1=min(ax+P,bx+P),min(ay+P,by+P)
    if x1-x0<32 or y1-y0<32:return None
    return a[y0-ay:y1-ay,x0-ax:x1-ax],b[y0-by:y1-by,x0-bx:x1-bx]

def registration(raw,r,c,placed):
    nominal=(c*C,r*C)
    # All first-column coordinates are fixed to the existing c08 boundary.
    if c==0:return (0,0),{'decision':'fixed_west_column','actualShiftXY':[0,0]}
    neighbours=[placed[k] for k in ((r,c-1),(r-1,c)) if k in placed]
    def score(dx,dy):
        scores=[]
        for old,position in neighbours:
            pair=overlap(old,position,raw,(nominal[0]+dx,nominal[1]+dy))
            if pair is None:continue
            a,b=pair
            # Subsample only for the metric; rendered pixels are never resampled.
            d=a[8:-8:3,8:-8:3].astype(np.float32)-b[8:-8:3,8:-8:3]
            d-=np.median(d,axis=(0,1),keepdims=True)
            ga=gradient(a)[8:-8:3,8:-8:3];gb=gradient(b)[8:-8:3,8:-8:3]
            scores.append(float(np.minimum(np.abs(d),48).mean()+.35*np.minimum(np.abs(ga-gb),48).mean()))
        return float(np.mean(scores)) if scores else 1e9
    xs=range(0,MAX_SHIFT+1) if c==3 else range(-MAX_SHIFT,MAX_SHIFT+1)
    ys=range(-MAX_SHIFT,1) if r==0 else (range(0,MAX_SHIFT+1) if r==3 else range(-MAX_SHIFT,MAX_SHIFT+1))
    candidates=sorted((score(dx,dy),dx,dy) for dy in ys for dx in xs)
    zero=score(0,0);best,dx,dy=candidates[0];second=candidates[1][0]
    improvement=(zero-best)/max(zero,1e-6);gap=(second-best)/max(zero,1e-6)
    reliable=(dx!=0 or dy!=0) and improvement>=.06 and gap>=.006
    shift=(dx,dy) if reliable else (0,0)
    return shift,{'decision':'bounded_integer_shift' if reliable else 'retain_nominal_unreliable_or_no_gain',
        'actualShiftXY':list(shift),'bestProposedShiftXY':[dx,dy],'zeroScore':zero,'bestScore':best,
        'secondScore':second,'relativeImprovement':improvement,'relativeBestGap':gap,
        'requiredImprovement':.06,'requiredBestGap':.006,'candidates':[[x,y,s] for s,x,y in candidates]}

def minimum_path(cost):
    """Top-to-bottom 8-connected minimum-cost path, one original-pixel step per row."""
    height,width=cost.shape;previous=cost[0].astype(np.float64).copy()
    parent=np.zeros((height,width),np.int8)
    for y in range(1,height):
        left=np.r_[np.inf,previous[:-1]];right=np.r_[previous[1:],np.inf]
        stacked=np.stack((left,previous,right));choice=np.argmin(stacked,axis=0)
        parent[y]=choice-1;previous=cost[y]+np.min(stacked,axis=0)
    path=np.empty(height,np.int16);path[-1]=int(np.argmin(previous))
    for y in range(height-1,0,-1):path[y-1]=path[y]+parent[y,path[y]]
    return path

def local_bias(a,b,valid,vertical=True):
    """Robust local RGB estimates along a seam; interpolation affects fields only."""
    if not vertical:a,b,valid=a.transpose(1,0,2),b.transpose(1,0,2),valid.T
    diff=a.astype(np.float32)-b.astype(np.float32)
    reliable=valid & (gradient(a)<18) & (gradient(b)<18) & (np.max(np.abs(diff),axis=2)<48)
    old_material,new_material=material(a),material(b)
    same=old_material==new_material
    # A foliage estimate must never recolour the neighbouring warm paving.
    fallbacks=[]
    for label in range(2):
        values=diff[reliable & same & (new_material==label)]
        fallbacks.append(np.clip(np.median(values,axis=0),-MAX_TONE,MAX_TONE) if len(values)>=64 else np.zeros(3))
    centres=[];bias=[]
    for begin in range(0,len(a),64):
        end=min(begin+64,len(a));local=[]
        for label in range(2):
            mask=reliable[begin:end]&same[begin:end]&(new_material[begin:end]==label)
            values=diff[begin:end][mask]
            local.append(np.clip(np.median(values,axis=0),-MAX_TONE,MAX_TONE) if len(values)>=24 else fallbacks[label])
        centres.append((begin+end-1)/2)
        bias.append(local)
    bias=np.asarray(bias);axis=np.arange(len(a))
    return np.stack([np.stack([np.interp(axis,centres,bias[:,label,k]) for k in range(3)],axis=1) for label in range(2)],axis=1).astype(np.float32)

def seam_cost(a,b,valid):
    cost=np.mean(np.abs(a.astype(np.float32)-b.astype(np.float32)),axis=2)
    cost+=.25*np.abs(gradient(a)-gradient(b))
    cost[~valid]=1000
    # Exclude the outermost 8 pixels, leaving space for the 6px transition.
    cost[:,:8]+=1000;cost[:,-8:]+=1000
    cost+=.003*np.abs(np.arange(cost.shape[1])[None,:]-(cost.shape[1]-1)/2)
    return cost

def region_field(height,width,path,bias,vertical,classes):
    if vertical:
        distance=np.abs(np.arange(width)[None,:]-path[:,None])
        weight=1-smoothstep(distance/FADE)
        return bias[np.arange(height)[:,None],classes]*weight[:,:,None],weight
    distance=np.abs(np.arange(height)[:,None]-path[None,:])
    weight=1-smoothstep(distance/FADE)
    return bias[np.arange(width)[None,:],classes]*weight[:,:,None],weight

def make_join(raw,old,valid,has_left,has_top,left_width,top_height,west_fixed,global_x,global_y,terminate_right=False):
    height,width=raw.shape[:2];paths={};details=[];classes=material(raw)
    # Initial paths locate a local field; recompute paths once after that field.
    if has_left:
        lw=min(left_width,width)
        path=minimum_path(seam_cost(old[:,:lw],raw[:,:lw],valid[:,:lw]))
        bias=local_bias(old[:,:lw],raw[:,:lw],valid[:,:lw])
        paths['left']=(path,lw,bias)
    if has_top:
        th=min(top_height,height)
        path=minimum_path(seam_cost(old[:th].transpose(1,0,2),raw[:th].transpose(1,0,2),valid[:th].T))
        bias=local_bias(old[:th],raw[:th],valid[:th],False)
        paths['top']=(path,th,bias)
    if west_fixed:
        boundary=H-global_x
        mask=valid[:,:boundary].copy()
        yy=np.arange(height)+global_y;mask[(yy<H)|(yy>=H+4096)]=False
        bias=local_bias(old[:,:boundary],raw[:,:boundary],mask)
        fixed_path=np.full(height,boundary,np.int16)
        paths['west_fixed']=(fixed_path,boundary,bias)
    initial_paths={k:v[0].copy() for k,v in paths.items()}
    def render_fields():
        fields=[];weights=[]
        for direction,(path,extent,bias) in paths.items():
            f,w=region_field(height,width,path,bias,direction!='top',classes)
            fields.append(f);weights.append(w)
        field=np.zeros_like(raw,dtype=np.float32)
        if fields:
            # Intersecting fields cannot add up beyond the per-channel bound.
            divisor=np.maximum(1,np.sum(weights,axis=0))[:,:,None]
            field=np.clip(np.sum(fields,axis=0)/divisor,-MAX_TONE,MAX_TONE)
        return np.clip(np.rint(raw.astype(np.float32)+field),0,255).astype(np.uint8)
    # Refine paths with tone compensation, then rebuild the saved field around
    # the actual final paths. The field never remains attached to an old path.
    for iteration in range(2):
        corrected=render_fields()
        for direction,(path,extent,bias) in list(paths.items()):
            if direction=='west_fixed':continue
            cost=seam_cost(old[:,:extent],corrected[:,:extent],valid[:,:extent]) if direction=='left' else seam_cost(old[:extent].transpose(1,0,2),corrected[:extent].transpose(1,0,2),valid[:extent].T)
            paths[direction]=(minimum_path(cost),extent,bias)
    corrected=render_fields()
    applied=corrected.astype(np.int16)-raw.astype(np.int16)
    assert np.max(np.abs(applied))<=MAX_TONE
    alpha=np.ones((height,width),np.float32)
    for direction,(path,extent,bias) in paths.items():
        if direction=='west_fixed':continue
        if direction=='left':
            alpha=np.minimum(alpha,np.clip((np.arange(width)[None,:]-path[:,None]+TRANSITION/2)/TRANSITION,0,1))
        else:
            alpha=np.minimum(alpha,np.clip((np.arange(height)[:,None]-path[None,:]+TRANSITION/2)/TRANSITION,0,1))
        details.append({'direction':direction,'overlapExtent':extent,'pathMin':int(path.min()),'pathMax':int(path.max()),'initialFinalPathMaxDifference':int(np.max(np.abs(path-initial_paths[direction]))),'toneCompensatedPathPasses':2})
    if terminate_right and has_top:
        # The row above already extends beyond this patch's right edge. Retain
        # that old context at the endpoint, using only a six-pixel transition,
        # so a later patch does not inherit an abrupt rectangular insert edge.
        ending=np.clip((width-1-np.arange(width)[None,:])/TRANSITION,0,1)
        alpha=np.minimum(alpha,ending)
        paths['right_termination']=(np.full(height,width-1-TRANSITION//2,np.int16),TRANSITION,np.zeros((height,3),np.float32))
        details.append({'direction':'right_termination','transitionWidth':TRANSITION,'existingPixelsOnly':True})
    alpha[~valid]=1
    if west_fixed:
        gx=np.arange(width)+global_x;gy=np.arange(height)+global_y
        alpha[(gy[:,None]>=H)&(gy[:,None]<H+4096)&(gx[None,:]<H)]=0
    alpha8=np.rint(alpha*255).astype(np.uint8)
    a=alpha8.astype(np.uint32)[:,:,None]
    joined=((old.astype(np.uint32)*(255-a)+corrected.astype(np.uint32)*a+127)//255).astype(np.uint8)
    return joined,alpha8,applied.astype(np.int8),paths,details

def save_contacts(core,west):
    q=OUT/'qa';q.mkdir(exist_ok=True);im=Image.fromarray(core)
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15);records=[]
    for axis in ('V','H'):
        for segment in range(4):
            size=(984,1064) if axis=='V' else (1024,1104)
            sheet=Image.new('RGB',size,'#eeeeee');draw=ImageDraw.Draw(sheet);boxes=[]
            for k in range(1,4):
                line=k*C;s=segment*C
                box=(line-160,s,line+160,s+C) if axis=='V' else (s,line-160,s+C,line+160)
                xy=((k-1)*332,40) if axis=='V' else (0,(k-1)*372+40)
                sheet.paste(im.crop(box),xy);draw.text((xy[0]+4,xy[1]-30),f'{axis} line={line} segment={segment+1}',fill='black',font=font)
                boxes.append({'localCoreBox':box,'sheetXY':xy})
            p=q/f'{axis}_segment{segment+1:02d}_1to1.png';sheet.save(p);records.append({**info(p),'boxes':boxes,'viewed':False,'resized':False})
    sheet=Image.new('RGB',(984,1104),'#eeeeee');draw=ImageDraw.Draw(sheet);boxes=[]
    for r in range(1,4):
        for c in range(1,4):
            x,y=c*C,r*C;box=(x-160,y-160,x+160,y+160);xy=((c-1)*332,(r-1)*372+40)
            sheet.paste(im.crop(box),xy);draw.text((xy[0]+4,xy[1]-30),f'J {x},{y}',fill='black',font=font);boxes.append({'localCoreBox':box,'sheetXY':xy})
    p=q/'junctions_1to1.png';sheet.save(p);records.append({**info(p),'boxes':boxes,'viewed':False,'resized':False})
    for r in range(4):
        p=q/f'west_shared_segment{r+1:02d}_1to1.png'
        strip=np.concatenate((west[r*C:(r+1)*C,-160:],core[r*C:(r+1)*C,:160]),axis=1)
        Image.fromarray(strip).save(p);records.append({**info(p),'westYRange':[r*C,(r+1)*C],'viewed':False,'resized':False})
    return records

def run(expected,reuse_registration=False):
    if not expected or len(expected)!=64:raise ValueError('--expected-r03-sha must be the writer-confirmed final SHA256')
    if sha(NATIVE/'r03_c01.png')!=expected:raise ValueError('r03_c01 is not the explicitly confirmed final version')
    sources=[];arrays={}
    for r in range(4):
        for c in range(4):
            patch=f'r{r+1:02d}_c{c+1:02d}';p=NATIVE/(patch+'.png');rec=p.with_name(p.name+'.generation.json')
            record=read(rec);digest=sha(p)
            if record.get('sha256')!=digest:raise ValueError(f'Unstable or mismatched source record: {patch}')
            arr=image_array(p)
            if arr.shape!=(P,P,3):raise ValueError(f'Incorrect native size: {patch}')
            arrays[(r,c)]=arr;sources.append({'patchId':patch,**info(p),'generationRecord':info(rec)})
    cached={};cache_hash=None
    if reuse_registration:
        prior=read(OUT/'assembly.json');cache_hash=sha(OUT/'assembly.json')
        if [(s['patchId'],s['sha256']) for s in prior['sources']]!=[(s['patchId'],s['sha256']) for s in sources]:raise ValueError('Cannot reuse registration: source SHA set changed')
        if prior['parameters']['integerTranslationMax']!=MAX_SHIFT:raise ValueError('Registration bound changed')
        cached={step['patchId']:step['registration'] for step in prior['steps']}
    handoff=read(ROOT/'handoff.json')
    west_entry=next(e for e in handoff['currentCandidates'] if e['tile']=='r08_c08')
    west_path=Path(west_entry['file']);west=image_array(west_path)
    if sha(west_path)!=west_entry['sha256'] or west.shape!=(4096,4096,3):raise ValueError('Fixed west reference failed SHA/size check')
    OUT.mkdir(exist_ok=True);(OUT/'masks').mkdir(exist_ok=True);(OUT/'fields').mkdir(exist_ok=True)
    canvas=np.zeros((S,S,3),np.uint8);valid=np.zeros((S,S),bool);owner=np.zeros((S,S),np.uint8)
    canvas[H:H+4096,:H]=west[:,-H:];valid[H:H+4096,:H]=True;owner[H:H+4096,:H]=255
    placed={};steps=[]
    for r in range(4):
        for c in range(4):
            patch=f'r{r+1:02d}_c{c+1:02d}';raw=arrays[(r,c)]
            if patch in cached:
                reg={**cached[patch],'reusedFromAssemblySha256':cache_hash};shift=reg['actualShiftXY']
            else:shift,reg=registration(raw,r,c,placed)
            dx,dy=shift;px,py=c*C+dx,r*C+dy
            placed[(r,c)]=(raw,(px,py))
            x0,y0=max(0,px),max(0,py);x1,y1=min(S,px+P),min(S,py+P)
            clipped=raw[y0-py:y1-py,x0-px:x1-px];old=canvas[y0:y1,x0:x1].copy();mask=valid[y0:y1,x0:x1].copy()
            lw=placed[(r,c-1)][1][0]+P-x0 if c else 0
            th=placed[(r-1,c)][1][1]+P-y0 if r else 0
            joined,alpha,field,paths,detail=make_join(clipped,old,mask,c>0,r>0,lw,th,c==0,x0,y0,c<3)
            canvas[y0:y1,x0:x1]=joined;valid[y0:y1,x0:x1]=True
            owner_view=owner[y0:y1,x0:x1];owner_view[alpha>=128]=r*4+c+1
            mask_path=OUT/'masks'/f'{patch}.incoming-alpha.png';Image.fromarray(alpha).save(mask_path)
            field_path=OUT/'fields'/f'{patch}.rgb-field.npz'
            np.savez_compressed(field_path,rgbDelta=field,sourceOriginXY=np.array([px,py]),canvasBox=np.array([x0,y0,x1,y1]))
            pathfile=OUT/'masks'/f'{patch}.paths.npz'
            np.savez_compressed(pathfile,**{k:v[0] for k,v in paths.items()})
            steps.append({'patchId':patch,'registration':reg,'nominalOriginXY':[c*C,r*C],'actualOriginXY':[px,py],
                'canvasBox':[x0,y0,x1,y1],'sourceCrop':[x0-px,y0-py,x1-px,y1-py],
                'incomingAlpha':info(mask_path),'actualRGBField':info(field_path),'seamPaths':info(pathfile),
                'seams':detail,'maxAppliedChannelCorrection':int(np.max(np.abs(field.astype(np.int16)))),
                'pixelsWithColorCorrection':int(np.any(field!=0,axis=2).sum()),'narrowBlendPixels':int(((alpha>0)&(alpha<255)).sum())})
            print(json.dumps({'patch':patch,'shift':list(shift),'maxTone':steps[-1]['maxAppliedChannelCorrection']}),flush=True)
    if not valid.all():raise AssertionError(f'Uncovered output pixels: {int((~valid).sum())}')
    if not np.array_equal(canvas[H:H+4096,:H],west[:,-H:]):raise AssertionError('Fixed west halo changed')
    for source in sources:
        if sha(source['file'])!=source['sha256']:raise ValueError(f"Source changed while assembling: {source['file']}")
        record=source['generationRecord']
        if sha(record['file'])!=record['sha256']:raise ValueError(f"Source record changed while assembling: {record['file']}")
    if sha(west_path)!=west_entry['sha256']:raise ValueError('West reference changed during assembly')
    padded=OUT/'candidate_with_halo.png';corepath=OUT/'candidate_4096.png';ownership=OUT/'masks'/'dominant-source.png'
    Image.fromarray(canvas).save(padded);core=canvas[H:H+4096,H:H+4096].copy();Image.fromarray(core).save(corepath);Image.fromarray(owner).save(ownership)
    qa=save_contacts(core,west)
    record={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c09','status':'candidate_pending_visual_review',
        'script':info(Path(__file__)),'sources':sources,'westFixedSource':west_entry,'parameters':{
            'nativeSize':P,'core':C,'halo':H,'overlap':230,'integerTranslationMax':MAX_SHIFT,'noResizing':True,
            'colorCorrectionMaxPerChannel':MAX_TONE,'localFieldFadePixels':FADE,'colorEstimateBinPixels':64,
            'colorMaterialGroups':['green foliage','non-foliage'],
            'transitionWidthPixels':TRANSITION,'minimumPathStepMaxPixels':1,
            'rightTerminationTransitionPixels':TRANSITION,
            'method':'row-major native overlap quilting; robust bounded translation only when reliable; local RGB fields; minimum-error path ownership; 6px transition',
            'westConstraint':'c08 read-only; exact last115px copied into padded west halo; first-column translations zero; core west color field fades over160px; no invented c08 pixels'},
        'steps':steps,'dominantSourceMask':{**info(ownership),'labels':'1..16 row-major source;255 fixed western c08. Fractional source weights are fully specified by sequential incoming-alpha masks.'},
        'outputs':[{'role':'candidate_with_halo','pixels':[4326,4326],**info(padded)},{'role':'candidate','pixels':[4096,4096],**info(corepath)}],
        'fixedWestHaloByteEqual':True,'sourcesUnchanged':True,'qa':qa,'qaAccepted':False,'clientAccepted':False,
        'unresolvedDefects':['Visual review pending; minimum paths and local color fields cannot establish missing structural geometry.','North, east and south neighbour tiles are absent from this scoped assembly.']}
    write(OUT/'assembly.json',record)
    for p in (padded,corepath):write(str(p)+'.generation.json',{'newGeneration':False,'operation':record['parameters']['method'],
        **info(p),'derivedFrom':sources+[west_entry],'assembly':info(OUT/'assembly.json'),'actualModel':None,'actualQuality':None,'accepted':False})
    print(json.dumps({'candidate':str(corepath),'assembly':str(OUT/'assembly.json'),'accepted':False}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-r03-sha',required=True,help='writer-confirmed final r03_c01 SHA; never run against an in-progress patch')
    parser.add_argument('--reuse-registration',action='store_true',help='reuse prior raw-overlap registration only when all source SHAs match exactly')
    args=parser.parse_args();run(args.expected_r03_sha,args.reuse_registration)

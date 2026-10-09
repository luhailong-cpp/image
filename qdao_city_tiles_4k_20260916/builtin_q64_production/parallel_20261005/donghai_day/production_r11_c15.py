"""r11_c15 bookkeeping and guides using exact global rectangle intersections."""
import sys, json
from pathlib import Path
from PIL import Image
import production as p
p.T=p.ROOT/'r11_c15'
STYLE=p.STYLE

def plan(): return p.loadj(p.T/'plan.json')
def status():
    d=plan(); names=list((p.T/'native').glob('r??_c??.png'))
    state={'tile':d['tile'],'globalRect':d['globalRect'],'updatedAtUtc':p.now(),'nativePatchesSaved':len(names),'nativePatchesRequired':16,'countsAsCompleteTile':False,'formalAccepted':False,'structureReferenceAvailable':(p.T/'guides/local-structure.png').is_file(),'northBindingStatus':d['neighbors']['north']['bindingStatus'],'phase':'native_expansion_in_progress' if names else 'structure_preparation'}
    p.savej(p.T/'progress.json',state);p.savej(p.T/'current-work.json',state)
p.status=status

def checked_neighbor(direction):
    d=plan()['neighbors'][direction]
    if d.get('bindingStatus')!='bound' or not d.get('sha256'):
        raise ValueError(direction+' neighbor is not bound; final native top row requires complete north tile.')
    path=Path(d['file'])
    if not path.is_file() or p.sha(path)!=d['sha256']:raise ValueError('Bound neighbor source missing/changed: '+direction)
    with Image.open(path) as im:
        im.load()
        if im.size!=(4096,4096):raise ValueError('Complete neighbor must be 4096x4096')
    return d

def bind_neighbor(direction,source,expected):
    d=plan();n=d['neighbors'][direction];source=Path(source).resolve()
    if not source.is_relative_to(p.ROOT.resolve()):raise ValueError('Neighbor source must remain in this task')
    if source.name!=n['tile']+'.png':raise ValueError('Neighbor filename disagrees with planned identity')
    if not source.is_file() or p.sha(source)!=expected:raise ValueError('Requested SHA is not the current neighbor source')
    with Image.open(source) as im:
        im.load()
        if im.size!=(4096,4096):raise ValueError('Neighbor must be a complete 4096 square')
    if n.get('sha256') not in (None,expected):raise ValueError('Refusing silent source rebinding')
    n.update(file=str(source),sha256=expected,bindingStatus='bound',boundAtUtc=p.now())
    if direction=='north':d['northBindingStatus']='bound'
    p.savej(p.T/'plan.json',d);status();print('Bound '+direction+' '+expected)

def overlap(a,b):
    x0=max(a[0],b[0]);y0=max(a[1],b[1]);x1=min(a[2],b[2]);y1=min(a[3],b[3])
    return (x0,y0,x1,y1) if x1>x0 and y1>y0 else None

def guide(row,column):
    if row not in range(1,5) or column not in range(1,5):raise ValueError('Native row and column must be 1..4')
    name=f'r{row:02d}_c{column:02d}'
    if (p.T/'native'/f'{name}.png').exists():raise ValueError('Preserve existing native and its reference guide')
    d=plan();x,y,_,_=d['globalRect'];ox=(column-1)*1024;oy=(row-1)*1024
    if row==1:checked_neighbor('north')
    box=(x-115+ox,y-115+oy,x+1139+ox,y+1139+oy)
    structure=p.T/'guides/local-structure.png'
    with Image.open(structure) as im:
        scale=im.width/4326
        g=im.convert('RGB').transform((1254,1254),Image.Transform.EXTENT,tuple(v*scale for v in (ox,oy,ox+1254,oy+1254)),Image.Resampling.BICUBIC)
    refs=[{'file':str(structure),'sha256':p.sha(structure),'role':'reference-only enlarged structural guide; not final pixels'}]
    def paste(path,rect,role):
        hit=overlap(box,rect)
        if hit:
            a,b,c,e=hit
            with Image.open(path) as im:g.paste(im.crop((a-rect[0],b-rect[1],c-rect[0],e-rect[1])),(a-box[0],b-box[1]))
            refs.append({'file':str(path),'sha256':p.sha(path),'role':role,'sourceGlobalRectXYXY':list(rect),'copiedGlobalIntersectionXYXY':list(hit),'resampled':False})
    for direction,n in d['neighbors'].items():
        if n['bindingStatus']!='bound':continue
        n=checked_neighbor(direction);nx,ny,nw,nh=n['globalRect']
        paste(Path(n['file']),(nx,ny,nx+nw,ny+nh),'actual complete '+direction+' neighboring tile pixels, intersection only')
    # Explicitly bound partial east natives are real pixels, never promoted to a whole tile.
    for ext in d.get('externalNativeBindings', []):
        path=Path(ext['file'])
        if not path.is_file() or p.sha(path)!=ext['sha256']:raise ValueError('Bound external native changed: '+str(path))
        if p.sha(ext['record'])!=ext['recordSha256']:raise ValueError('Bound external record changed: '+str(path))
        paste(path,tuple(ext['globalRectXYXY']),ext['role'])
    for rr,cc in [(row-1,column-1),(row-1,column),(row-1,column+1),(row+1,column-1),(row+1,column),(row+1,column+1),(row,column+1),(row,column-1)]:
        src=p.T/'native'/f'r{rr:02d}_c{cc:02d}.png'
        if not src.exists():continue
        sx=x-115+(cc-1)*1024;sy=y-115+(rr-1)*1024
        paste(src,(sx,sy,sx+1254,sy+1254),'actual overlapping same-tile native neighbor pixels')
    path=p.T/'guides'/f'{name}.png';g.save(path)
    record={'file':str(path),'sha256':p.sha(path),'operation':'reference-only structure crop plus exact global rectangle intersections of verified neighbor pixels','derivedFrom':refs,'globalBox':list(box),'allowedInFinal':False,'resampledNativeContext':False}
    p.savej(str(path)+'.generation.json',record)
    return path

def save_prompt(name,prompt,target,role):
    refs=[{'file':str(target),'role':role},{'file':str(STYLE),'role':'primary user-confirmed rounded hand-painted style and materials; no UI'}]
    for ref in refs:ref['sha256']=p.sha(ref['file'])
    (p.T/'prompts'/f'{name}.txt').write_text(prompt,encoding='utf-8');p.savej(p.T/'prompts'/f'{name}.references.json',refs)
    print(json.dumps({'name':name,'prompt':prompt,'references':[r['file'] for r in refs]}))

def prepare_structure():
    if (p.T/'guides/local-structure.png').exists():raise ValueError('Structure reference already exists')
    prompt='Edit IMAGE1 only. This is the exact confirmed local layout crop of a fishing-village pier, a reference-only structural view. Preserve camera, scale, framing, all original silhouettes, object positions and counts. The lower half is a warm timber pier with wide diagonal planks, a thick front edge and several original cropped blue-gray-capped wooden mooring piles. At center stands the existing tall wooden lifting frame: tall rear upright at upper-right, a shorter left upright, curved sloping top member and one diagonal middle crossbar, with the same simple hanging pale ropes; keep the frame asymmetry and connections, do not make a gate or add a roof. Preserve the left slim orange-brown post with its long vertical red hanging decoration and pale-gold decorative marks, the small dark capped bollard behind it, the original sagging pale edge rope and small tie points. Preserve the single short blue-gray squared block at the frame foot. Upper background is quiet clear blue/cyan water; at the cropped top-right is the original blue-gray stone retaining wall and localized pale contact water marks. Keep this water broad and calm, no repeating waves, white net/caustic grid or noise. Preserve the existing wood-frame cast shadows across the deck. Do not add ropes, posts, plank divisions, lanterns, boats, text or objects. IMAGE2 is the PRIMARY confirmed style reference: rounded bright clean Q-style painted wood/stone with generous volume, crisp controlled outlines and soft clean directional shadows. Existing cropped objects must remain cropped at identical edges. Native opaque1254x1254; no UI, border, zoom, crop or viewpoint change. Redraw the structure cleanly while retaining its exact confirmed geometry. This is only a local structure reference, not final enlarged HD art.'
    save_prompt('local-structure',prompt,p.T/'guides/local-layout.png','edit target; confirmed low-resolution layout crop for structural reference only')

def prepare(row,column):
    target=guide(row,column)
    prompt='Edit IMAGE1 only, a precise cropped fragment of an existing fishing-village map. Preserve the camera, exact framing, EVERY original material silhouette, object count and placement. Objects cut by the bottom or sides must continue out of the image at the same edges: never invent a complete object, a base, a new waterline or a lower end for cropped piles, posts, stone or wood. Water must occupy ONLY already-blue existing water regions; never replace timber, dark supports or shadows with water. Redraw the shown soft geometry clearly at native detail, with the same sparse structural joints, broad plank faces, ropes or decoration only where already visible. Retain original material colors, scale and directional cast shadows. Sharp edge strips are actual already-generated native neighbors: continue real contours and material color across their soft/sharp transitions; no straight tonal seam, doubled edge or new object at the reference boundary. IMAGE2 is the PRIMARY confirmed bright clean rounded Q-style hand-painted rendering reference; clean generous volume, restrained broad painted texture and controlled outlines. Do not borrow UI or objects from it. No new wood divisions, posts, fittings, writing, foam, white water grid, tiny waves or noise. Keep any existing water broad and low-contrast. One opaque native1254x1254 image. No zoom, crop, camera change, border, blur filter, texture noise, enlargement or completed cropped objects.'
    save_prompt(f'r{row:02d}_c{column:02d}',prompt,target,'edit target; exact field of view, reference-only interior with actual native neighboring strips')

if __name__=='__main__':
    command=sys.argv[1]
    if command=='prepare-structure':prepare_structure()
    elif command=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
    elif command=='record':
        with Image.open(sys.argv[3]) as im:
            im.load()
            if im.size!=(1254,1254):raise ValueError('Native output must be1254x1254; never upscale')
        refs=p.loadj(p.T/'prompts'/(sys.argv[2]+'.references.json'))
        assert all(p.sha(v['file'])==v['sha256'] for v in refs)
        p.record(sys.argv[2],sys.argv[3])
    elif command=='bind-neighbor':bind_neighbor(sys.argv[2],sys.argv[3],sys.argv[4])
    elif command=='status':status()
    else:raise SystemExit('Expected prepare-structure, prepare, record, bind-neighbor or status')

"""r07_c15 bookkeeping and guides using exact global rectangle intersections."""
import sys, json
from pathlib import Path
from PIL import Image
import production as p
p.T=p.ROOT/'r07_c15'
STYLE=p.STYLE

def plan(): return p.loadj(p.T/'plan.json')
def status():
    d=plan(); names=list((p.T/'native').glob('r??_c??.png'))
    state={'tile':d['tile'],'globalRect':d['globalRect'],'updatedAtUtc':p.now(),'nativePatchesSaved':len(names),'nativePatchesRequired':16,'countsAsCompleteTile':False,'formalAccepted':False,'structureReferenceAvailable':(p.T/'guides/local-structure.png').is_file(),'southBindingStatus':d['neighbors']['south']['bindingStatus'],'phase':'native_expansion_in_progress' if names else 'structure_preparation'}
    p.savej(p.T/'progress.json',state);p.savej(p.T/'current-work.json',state)
p.status=status

def checked_neighbor(direction):
    d=plan()['neighbors'][direction]
    if d.get('bindingStatus')!='bound' or not d.get('sha256'):
        raise ValueError(direction+' neighbor is not bound; final native bottom row requires complete south tile.')
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
    if direction=='south':d['southBindingStatus']='bound'
    p.savej(p.T/'plan.json',d);status();print('Bound '+direction+' '+expected)

def overlap(a,b):
    x0=max(a[0],b[0]);y0=max(a[1],b[1]);x1=min(a[2],b[2]);y1=min(a[3],b[3])
    return (x0,y0,x1,y1) if x1>x0 and y1>y0 else None

def guide(row,column):
    if row not in range(1,5) or column not in range(1,5):raise ValueError('Native row and column must be 1..4')
    name=f'r{row:02d}_c{column:02d}'
    if (p.T/'native'/f'{name}.png').exists():raise ValueError('Preserve existing native and its reference guide')
    d=plan();x,y,_,_=d['globalRect'];ox=(column-1)*1024;oy=(row-1)*1024
    if row==4:checked_neighbor('south')
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
    # Exact adjacent native context may be used before the east 4K is assembled.
    # Its full native coordinate extent and identity remain explicit evidence.
    if column==4 and d['neighbors']['east']['bindingStatus']!='bound':
        nx,ny,_,_=d['neighbors']['east']['globalRect']
        for er in range(1,5):
            src=p.ROOT/'r07_c16/native'/f'r{er:02d}_c01.png'
            if not src.is_file():continue
            record=p.loadj(str(src)+'.generation.json')
            if p.sha(src)!=record['sha256'] or [record['width'],record['height']]!=[1254,1254]:raise ValueError('Changed east native source')
            sx=nx-115;sy=ny-115+(er-1)*1024
            paste(src,(sx,sy,sx+1254,sy+1254),'actual adjacent east native patch, not yet a complete neighboring tile; exact global overlap')
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
    prompt='Edit IMAGE 1 only. This is a structural reference crop from an existing bright Daoist Q-style fishing-village map. Preserve the exact camera, crop, composition and every existing structural footprint. Keep the pictured upper timber pier, every existing tall round piling and railing post, deck plank direction, the small dark ladder under its front edge, and each existing contact highlight/shadow in the water. Keep the lower cropped boat cabin roof, framing, blue panel, mooring ropes and capped posts exactly in place. Clarify ONLY those already pictured objects in the confirmed rounded, clean, warm hand-painted material style of IMAGE 2. Do not add extra posts, ladders, planks, ropes, roofs, new objects or decorations; do not move or change any silhouette. Keep water calm blue/cyan with broad low-contrast soft shading and existing pier shadows; no new white caustic nets, small sharp wave contours, grain or foam. Keep all real cast shadows and original daylight direction. No characters, labels, UI, text, border or zoom. One opaque native1254 square, identical field of view. This is structure reference only, not enlarged final pixels.'
    save_prompt('local-structure',prompt,p.T/'guides/local-layout.png','edit target; confirmed low-resolution layout crop for structural reference only')

def prepare(row,column):
    target=guide(row,column)
    prompt='''Use case: precise-object-edit. Edit IMAGE 1 only for a native-pixel crop of a bright clean rounded Q-style fishing village. Preserve the quiet smooth blue/cyan WATER as broad soft low-contrast color fields. Do not add water details, ripple contours, cells, foam, bright streaks, wave blocks, caustic lines, pale patches or grain. This calm blue plane is intentional final art. Polish only existing pictured cropped boat, timber, mast or rope if present, retaining every original shape, position, outline, proportion, color and light. No new object, structure, rope, plank joint or decoration. Sharp strips at any edge are actual already generated neighboring context: preserve their geometry and colors, continue smoothly across the sharp/soft boundary without a line. Do not treat the strip boundary as a physical object. If the crop only contains water, return quiet water only. IMAGE 2 is the PRIMARY confirmed style: controlled clean outlines, rounded volumes, warm hand-painted timber; no UI. Keep the camera and crop fixed. One opaque 1254x1254 native image, highest available finish, no text, characters, border, crop, zoom, blur filter, oversharpening or photoreal texture.'''
    prompt+=' Preserve every already-present contact highlight, broad water reflection and dark cast shadow as real required scene features; restrictions on adding water detail never mean deleting these existing features. Preserve all pictured objects including any small dark ladder beneath the pier; never mistake a shadow or ladder for a resolution artifact.'
    if row==4:
        prompt+=' The bottom115 pixel strip is the FINAL already-completed south tile, so its geometry and material are mandatory anchors. Reconcile the softer structural guide just above it into the exact already-sharp shapes at that bottom edge. If a barrel, roof panel, rope or plank enters from that bottom strip, continue that SAME object upward naturally within this crop; never leave the strip as an abrupt pasted collage, hard horizontal line or disconnected object. Bottom strip takes precedence over conflicting soft-guide interior geometry. Preserve all top neighboring context and the overall footprint.'
    save_prompt(f'r{row:02d}_c{column:02d}',prompt,target,'edit target; exact field of view, reference-only interior with actual native neighboring strips')

if __name__=='__main__':
    command=sys.argv[1]
    if command=='prepare-structure':prepare_structure()
    elif command=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
    elif command=='record':p.record(sys.argv[2],sys.argv[3])
    elif command=='bind-neighbor':bind_neighbor(sys.argv[2],sys.argv[3],sys.argv[4])
    elif command=='status':status()
    else:raise SystemExit('Expected prepare-structure, prepare, record, bind-neighbor or status')

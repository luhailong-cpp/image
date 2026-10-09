"""r10_c15 bookkeeping and guides using exact global rectangle intersections."""
import sys, json
from pathlib import Path
from PIL import Image
import production as p
p.T=p.ROOT/'r10_c15'
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
    prompt='Edit IMAGE1 only. This is an exact local layout crop of the confirmed fishing-village map, a reference-only structural view. Preserve camera, scale, framing, positions, footprints, steps and cast shadows. Render the existing pale warm cream stone platform with its gently angled front lip, curved dark blue-gray masonry retaining wall below it, the low pale curved stone edge at the cropped top with a small cyan water sliver, the existing cropped wooden building/pier edge at right with its broad cool-gray cast shadow. Preserve the three short round wooden bollards at upper-left, center and lower-right, their original brown/red-brown colors, and the same thin pale sagging rope connections. Preserve the single tall cropped foreground left wooden mooring post with a small blue-gray top, its unchanged position and small pale water-contact ring. Keep partial edge objects cropped. Preserve existing pale step/border shapes without inventing new stairs, bricks, rails, posts, boats or decorations. Keep the open lower-left blue water quiet, with broad soft low-contrast fields; the small existing contact highlight around the tall post stays localized, no repeating waves, white caustic grids, noise or new ripples. Follow IMAGE2 as PRIMARY confirmed rounded bright clean Q-style hand-painted materials: warm wood, substantial rounded stone blocks, controlled clear outlines, smooth volume and existing soft directional shadows. Retain sparse original masonry divisions and plank spacing rather than adding dense texture. No characters, text, UI, frame, zoom or crop. One opaque native1254x1254 image. This is only a local structure reference and never a final enlarged tile.'
    save_prompt('local-structure',prompt,p.T/'guides/local-layout.png','edit target; confirmed low-resolution layout crop for structural reference only')

def prepare(row,column):
    target=guide(row,column)
    prompt='Use case: precise-object-edit. Edit IMAGE1 only into a clean native-pixel map fragment. Preserve the exact existing layout, camera, framing, object count, geometry, colors and light. Draw only the pictured portions of pale stone platform/steps, curved blue-gray retaining wall and original sparse block joints, rounded wooden bollards and mooring post, existing rope connections, cropped wooden building edge, and their original shadows if present. No added blocks, plank divisions, stairs, posts, rope, boat or decoration. The original structure can be large and cropped by the frame: do not complete or redesign it. When water is present keep it intentionally quiet, broad smooth blue/cyan low-contrast fields, no grid, caustic pattern, noise, ripples, pale streaks or foam except the original small contact ring where shown. Existing sharp edge strips are actual verified neighboring native pixels; preserve their geometry and far-edge colors and continue all real features across the soft/sharp transition without a straight color boundary or duplicated contour. Do not treat a reference-strip seam as a real object edge. Retain original directional cast shadows and soft clean volumes. IMAGE2 is the PRIMARY confirmed style: rounded bright clean Q-style painted timber and stone, crisp controlled outlines and clear generous forms, no photoreal texture. Return one opaque1254x1254 native image with fixed camera, no text/UI/characters/frame/crop/zoom/blur filter/oversharpening. Do not rescale the guide into a final image; redraw at native detail while preserving its composition.'
    save_prompt(f'r{row:02d}_c{column:02d}',prompt,target,'edit target; exact field of view, reference-only interior with actual native neighboring strips')

if __name__=='__main__':
    command=sys.argv[1]
    if command=='prepare-structure':prepare_structure()
    elif command=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
    elif command=='record':p.record(sys.argv[2],sys.argv[3])
    elif command=='bind-neighbor':bind_neighbor(sys.argv[2],sys.argv[3],sys.argv[4])
    elif command=='status':status()
    else:raise SystemExit('Expected prepare-structure, prepare, record, bind-neighbor or status')

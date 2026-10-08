"""r09_c15 bookkeeping and guides using exact global rectangle intersections."""
import sys, json
from pathlib import Path
from PIL import Image
import production as p
p.T=p.ROOT/'r09_c15'
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
    prompt='Edit IMAGE 1 only. This is the exact local layout crop of a bright clean rounded Daoist Q-style fishing village. Preserve its exact camera, framing, positions, footprints, proportions, structure and color palette. Preserve the existing timber pier entering from the upper-left, its planked top, heavy warm-brown horizontal edge beam, the tall thick posts, the existing blue cap on the upper-middle post and gray cap on the left post, the partly submerged support beneath the pier, and the cropped lower foreground light-timber rim/deck and posts. Preserve all existing gaps and the large open cyan-blue water at right. Do not turn the cropped foreground objects into new complete structures or add ropes, lanterns, poles, boats, planks or decorations. Render only these existing shapes into clear rounded hand-painted forms matching IMAGE 2, the PRIMARY confirmed style, with controlled clean outlines and warm timber. Keep the original broad blue shadows and existing small water-contact highlights at the post bases; elsewhere keep water intentionally quiet and smooth with broad soft low-contrast color fields. Do not add ripples, foam, bright lines, cells, white networks, noise or grain. Retain original plank spacing and broad wood forms, no dense grain. No text, UI, characters, border, zoom or crop. Return one opaque native1254 square of this exact view. This is a reference-only local structure image; it will not be enlarged into final pixels.'
    save_prompt('local-structure',prompt,p.T/'guides/local-layout.png','edit target; confirmed low-resolution layout crop for structural reference only')

def prepare(row,column):
    target=guide(row,column)
    prompt='''Use case: precise-object-edit. Edit IMAGE 1 only for a native-pixel crop of a bright clean rounded Q-style fishing village. Preserve the quiet smooth blue/cyan WATER as broad soft low-contrast color fields. Do not add water details, ripple contours, cells, foam, bright streaks, wave blocks, caustic lines, pale patches or grain. This calm blue plane is intentional final art. Polish only existing pictured cropped boat, timber, mast or rope if present, retaining every original shape, position, outline, proportion, color and light. No new object, structure, rope, plank joint or decoration. Sharp strips at any edge are actual already generated neighboring context: preserve their geometry and colors, continue smoothly across the sharp/soft boundary without a line. Do not treat the strip boundary as a physical object. If the crop only contains water, return quiet water only. Any perfectly straight water-color division at a neighboring-strip boundary is an unwanted guide seam; dissolve it into smooth continuous water while retaining the far-edge neighbor color. Existing small pale water-contact marks at pictured post bases are allowed and must remain in place. Keep original plank spacing and post/beam silhouettes; do not add joints. IMAGE 2 is the PRIMARY confirmed style: controlled clean outlines, rounded volumes, warm hand-painted timber; no UI. Keep the camera and crop fixed. One opaque 1254x1254 native image, highest available finish, no text, characters, border, crop, zoom, blur filter, oversharpening or photoreal texture.'''
    save_prompt(f'r{row:02d}_c{column:02d}',prompt,target,'edit target; exact field of view, reference-only interior with actual native neighboring strips')

if __name__=='__main__':
    command=sys.argv[1]
    if command=='prepare-structure':prepare_structure()
    elif command=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]))
    elif command=='record':p.record(sys.argv[2],sys.argv[3])
    elif command=='bind-neighbor':bind_neighbor(sys.argv[2],sys.argv[3],sys.argv[4])
    elif command=='status':status()
    else:raise SystemExit('Expected prepare-structure, prepare, record, bind-neighbor or status')

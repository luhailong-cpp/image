from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil, sys
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
REPO=Path('D:/work/image')
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare(pid,prev=None):
    guide=ROOT/'guides'/f'{pid}.png'
    target=guide
    if prev:
        source=OUT/f'{prev}.png'
        a=Image.open(guide).convert('RGB'); b=Image.open(source).convert('RGB')
        assert a.size==b.size==(1254,1254)
        a.paste(b.crop((1024,0,1254,1254)),(0,0))
        target=OUT/f'{pid}-target.png';a.save(target)
        write(str(target)+'.generation.json',dict(file=str(target),sha256=sha(target),createdAt=now(),width=1254,height=1254,format='PNG',derivedFrom=[dict(file=str(s),sha256=sha(s)) for s in [guide,source]],operation=dict(kind='guide_with_exact_left_neighbor_overlap',sourceBoxLTRB=[1024,0,1254,1254],destinationBoxLTRB=[0,0,230,1254],scale=1,noResampling=True),productionPixels=False))
    prompt=f'''Use case: precise-object-edit. Asset: Five Elements Tales (五行奇谈), island Mid-Autumn map r09_c13 native detail patch {pid}. Image 1 is the exact cropped geometry and lighting edit target. Image 2 is the main approved art-style reference ONLY: refined plump rounded clean hand-painted Taoist chibi material finish, never copy its text/UI. Repaint image 1 as new crisp native 1254 by 1254 pixel detailed map artwork, one opaque full-bleed square. Keep the exact same crop, camera, scale, all roof tile joints, masonry edges, stairs, railing, wood silhouettes, foliage occupancy, shadow direction, and exact edge crossings. Preserve its clear cool blue-violet evening stone, warm amber lamp glow, golden-orange curved roof tiles, rich rounded green foliage wherever shown. Refine clean soft stone bevels, smooth warm wood, distinct broad rounded leaves and crisp tile surfaces without adding objects or ornament. Maintain every important contour at the guide coordinate; do not shift, zoom, rotate, recenter, straighten, or redesign anything. No text, people, icons, border, watermark, grain, cracks, grit, sharpening halo or blur. '''
    if prev:
        prompt+='The leftmost 230-pixel strip of image 1 is the actual freshly generated neighboring patch at one source pixel per output pixel. Preserve that strip as exactly as possible and continue every leaf/stone/roof edge and light seamlessly to the right. Do not draw a vertical line at its boundary.'
    else:
        prompt+='The leftmost 115-pixel strip of image 1 is actual prior western neighbor context at one source pixel per output pixel. Preserve this strip and extend the roof and stone structures continuously rightward; reconcile the guide junction through genuine coherent drawing, no blurred band. Keep all core geometry to the right fixed.'
    pp=OUT/f'{pid}.prompt.txt'; pp.write_text(prompt+'\n',encoding='utf-8')
    params=dict(prompt=prompt,referenced_image_paths=[str(target),str(STYLE)],transparent_background=False)
    write(OUT/f'{pid}.call.json',params)
    print(json.dumps(dict(pid=pid,target=str(target),prompt=prompt,refs=params['referenced_image_paths'])))
def record(pid,source):
    source=Path(source);dest=OUT/f'{pid}.png'; shutil.copyfile(source,dest)
    im=Image.open(dest);im.verify();im=Image.open(dest)
    params=json.loads((OUT/f'{pid}.call.json').read_text(encoding='utf-8'))
    roles=['geometry edit target with actual left-neighbor context','main approved art style']
    data=dict(file=str(dest),sha256=sha(dest),generatedAt=now(),width=im.width,height=im.height,format=im.format,tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=params['referenced_image_paths']),actualModel=None,actualQuality=None,unverifiedReason='Host-managed; tool exposes no model/quality selectors and returns neither value.',evidence=dict(sourceOutputPath=str(source),sourceOutputSha256=sha(source),resultId=source.stem),prompt=str(OUT/f'{pid}.prompt.txt'),promptSha256=sha(OUT/f'{pid}.prompt.txt'),references=[dict(file=p,sha256=sha(p),role=roles[i]) for i,p in enumerate(params['referenced_image_paths'])],role='native_detail_patch_not_full_4K_tile',patchId=pid,nativeCore=1024,halo=115,resizedAfterGeneration=False,complete4KTile=False)
    write(str(dest)+'.generation.json',data)
    print(json.dumps(dict(file=str(dest),size=im.size,sha256=sha(dest))))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None)
    if sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])

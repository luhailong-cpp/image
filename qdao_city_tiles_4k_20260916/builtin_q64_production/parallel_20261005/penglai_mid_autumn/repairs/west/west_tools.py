from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,sys,shutil
from PIL import Image
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
REPO=Path('D:/work/image')
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prepare():
    h=json.loads((ROOT/'handoff.json').read_text(encoding='utf-8-sig'))
    old=Path(h['baselineCandidates'][2]['file']);new=ROOT/'assembly/r09_c13-candidate.png'
    a=Image.open(old).convert('RGB');b=Image.open(new).convert('RGB')
    assert a.size==b.size==(4096,4096)
    for i,y in enumerate([0,947,1894,2842],1):
        pid=f'west{i}';target=OUT/f'{pid}-target.png'
        im=Image.new('RGB',(1254,1254));im.paste(a.crop((3469,y,4096,y+1254)),(0,0));im.paste(b.crop((0,y,627,y+1254)),(627,0));im.save(target)
        write(str(target)+'.generation.json',dict(file=str(target),sha256=sha(target),createdAt=now(),width=1254,height=1254,format='PNG',derivedFrom=[dict(file=str(p),sha256=sha(p))for p in [old,new]],operation=dict(kind='native_crop_join_no_resampling',oldCropLTRB=[3469,y,4096,y+1254],newCropLTRB=[0,y,627,y+1254],joinX=627,globalRectXYWH=[48525,32768+y,1254,1254]),productionPixels=False))
        prompt=f'''Use case: precise-object-edit. Five Elements Tales (五行奇谈) island Mid-Autumn map, native west shared-edge repair {pid}. Image 1 is a real 1254 by 1254 pixel crop assembled from two adjacent map tiles, LEFT half x0..626 is the existing accepted-by-scope western neighbor and RIGHT half x627..1253 is the new tile with a visible join at x627. Image 2 is the main approved art-style reference only, clean plump rounded hand-painted Taoist chibi polish; never copy UI/text. Output one 1254 by 1254 opaque native square with exactly the same camera and crop. Repair ONLY the mismatched connection immediately to the RIGHT of x627, no more than 500 pixels into the right half. LEFT HALF MUST STAY THE SAME: all existing roof, rail, stairs, paving, shadows and colors there are hard geometric context, not material to redesign. Preserve the outermost 100 pixels and the rightmost 127 pixels as return context, and preserve overall building footprints and navigable passage widths. Genuinely redraw the missing local connections so every incoming timber edge, stone step, balustrade line, slab joint or roof ridge from the left continues coherently into the right. Remove the vertical discontinuity, duplicate contour or abrupt material transition by drawing the connecting geometry, never by blurring/feathering over it. Preserve crisp stone bevels, rounded golden-orange roof tiles, existing warm amber light and cool blue-violet night stone. Do not add or remove objects, change camera, add text/people/border, create grain/cracks or invent new road/architecture. Limit changes to that narrow right-hand seam repair corridor; keep the rest pixel-stable.'''
        pp=OUT/f'{pid}.prompt.txt';pp.write_text(prompt+'\n',encoding='utf-8')
        write(OUT/f'{pid}.call.json',dict(prompt=prompt,referenced_image_paths=[str(target),str(STYLE)],transparent_background=False))
    print(json.dumps(dict(prepared=4,newSourceSha256=sha(new),oldSourceSha256=sha(old))))
def record(pid,source):
    source=Path(source);dest=OUT/f'{pid}.png';shutil.copyfile(source,dest)
    im=Image.open(dest);im.verify();im=Image.open(dest)
    params=json.loads((OUT/f'{pid}.call.json').read_text(encoding='utf-8'))
    t=json.loads((OUT/f'{pid}-target.png.generation.json').read_text(encoding='utf-8'))
    write(str(dest)+'.generation.json',dict(file=str(dest),sha256=sha(dest),generatedAt=now(),width=im.width,height=im.height,format=im.format,tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8-sig')),submittedParameters=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=params['referenced_image_paths']),actualModel=None,actualQuality=None,unverifiedReason='Host-managed; tool exposes no model/quality selector and returns no reliable model/quality metadata.',evidence=dict(sourceOutputPath=str(source),sourceOutputSha256=sha(source),resultId=source.stem),prompt=str(OUT/f'{pid}.prompt.txt'),promptSha256=sha(OUT/f'{pid}.prompt.txt'),references=[dict(file=p,sha256=sha(p),role=('native joined geometry edit target' if i==0 else 'main approved art style')) for i,p in enumerate(params['referenced_image_paths'])],role='native_AI_seam_repair_pending_registration_and_mask_merge',patchId=pid,globalRectXYWH=t['operation']['globalRectXYWH'],requestedRepairLocalRectXYWH=[627,100,500,1054],resizedAfterGeneration=False,merged=False,formalAccepted=False))
    print(json.dumps(dict(file=str(dest),size=im.size,sha256=sha(dest))))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])

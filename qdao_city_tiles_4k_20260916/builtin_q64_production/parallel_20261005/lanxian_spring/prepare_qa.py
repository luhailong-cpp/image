from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
from PIL import Image
BASE=Path(__file__).resolve().parent
T=BASE/'r08_c09'
Q=T/'qa/root';Q.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
h=read(BASE/'handoff.json'); west=next(x for x in h['currentCandidates'] if x['tile']=='r08_c08')
wp=Path(west['file']);assert sha(wp)==west['sha256']
im=Image.open(T/'assembly/coverage.png').convert('RGB').crop((115,115,4211,4211))
w=Image.open(wp).convert('RGB')
pair=Image.new('RGB',(8192,4096));pair.paste(w,(0,0));pair.paste(im,(4096,0))
pair.resize((2048,1024),Image.Resampling.LANCZOS).save(BASE/'current-preview.png')
entries=[]
for i in range(4):
    box=(4096-384,i*1024,4096+384,(i+1)*1024)
    p=Q/f'west-seam-{i+1:02d}.png';pair.crop(box).save(p)
    entries.append({'file':str(p),'sha256':sha(p),'pairBoxXYXY':list(box),'role':'native_pixel_shared_edge_QA','viewed':False})
for axis in ['x','y']:
    for s in [1024,2048,3072]:
        for i in range(4):
            box=(s-128,i*1024,s+128,(i+1)*1024) if axis=='x' else (i*1024,s-128,(i+1)*1024,s+128)
            p=Q/f'internal-{axis}{s}-{i+1}.png';im.crop(box).save(p)
            entries.append({'file':str(p),'sha256':sha(p),'coreBoxXYXY':list(box),'role':'native_pixel_internal_seam_QA','viewed':False})
for y in [1024,2048,3072]:
    for x in [1024,2048,3072]:
        box=(x-128,y-128,x+128,y+128);p=Q/f'junction-{x}-{y}.png';im.crop(box).save(p)
        entries.append({'file':str(p),'sha256':sha(p),'coreBoxXYXY':list(box),'role':'native_pixel_junction_QA','viewed':False})
record={'createdAt':datetime.now(timezone.utc).isoformat(),'sourceWest':west,'sourceAssemblyManifest':str(T/'assembly/manifest.json'),'sourceAssemblyManifestSha256':sha(T/'assembly/manifest.json'),'images':entries,'formalAccepted':False}
(Q/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(BASE/'current-preview.png.generation.json').write_text(json.dumps({'file':str(BASE/'current-preview.png'),'sha256':sha(BASE/'current-preview.png'),'operation':'4096-square west + current native coverage assembled then downsampled to preview; checkerboard is missing pixels only','derivedFrom':[west,{'file':str(T/'assembly/coverage.png'),'sha256':sha(T/'assembly/coverage.png')}],'role':'current_work_preview_not_complete_city'},ensure_ascii=False,indent=2),encoding='utf-8')
print(len(entries))

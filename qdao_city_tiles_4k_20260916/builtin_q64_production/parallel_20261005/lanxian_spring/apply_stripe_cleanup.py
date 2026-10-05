from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
BASE=Path(__file__).resolve().parent
T=BASE/'r08_c09';JOB=T/'jobs/stripe-cleanup';R=T/'repairs/stripe-cleanup';R.mkdir(parents=True,exist_ok=True)
SRC=Path('C:/Users/luyua/.codex/generated_images/01a10bb2-5cf3-7db0-a7f1-5c85ef972ed1/exec-86bc5405-0fb2-48c9-813b-64213994d51b.png')
TARGET=T/'native/r03_c01.png';SIDECAR=Path(str(TARGET)+'.generation.json')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
current=read(SIDECAR);assert sha(TARGET)==current['sha256']
old=read(R/'before-source-record.json') if (R/'before-source-record.json').exists() else current
write(R/'before-source-record.json',old)
raw=R/'native.png';shutil.copyfile(SRC,raw)
new=Image.open(raw).convert('RGB');originalPath=Path(old['derivedFrom'][0]['file']);assert sha(originalPath)==old['sha256'];original=Image.open(originalPath).convert('RGB');assert new.size==original.size==(1254,1254)
prompt=(JOB/'prompt.txt').read_text(encoding='utf-8-sig')
request=read(JOB/'request.json');receipt=read(JOB/'tool-result.json')
record={'schemaVersion':1,'file':str(raw),'sha256':sha(raw),'generatedAt':receipt['completedAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(BASE.parents[3]/'config/image-generation.json'),'submittedParameters':dict(request,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host exposes no model/quality selector or returned version.','originalToolResultImagePath':str(SRC),'evidence':str(JOB/'tool-result.json'),'prompt':str(JOB/'prompt.txt'),'references':[{'path':str(TARGET),'sha256':old['sha256'],'role':'edit target at submission; original bytes remain at day source','sourceCounterpart':str(BASE.parent/'lanxian_day/r08_c09/native/r03_c01.png')},{'path':'D:/work/image/designs/gameplay-ui/04-guild.png','sha256':sha(Path('D:/work/image/designs/gameplay-ui/04-guild.png')),'role':'primary confirmed art style'}]}
write(Path(str(raw)+'.generation.json'),record)
polygons=[[(169,79),(688,47),(778,570),(172,603)],[(180,677),(791,648),(862,1085),(191,1132)]]
binary=Image.new('L',(1254,1254),0);draw=ImageDraw.Draw(binary)
for poly in polygons:draw.polygon(poly,fill=255)
mask=np.zeros((1254,1254),dtype=np.float32)
eroded=binary
for _ in range(2):
    eroded=eroded.filter(ImageFilter.MinFilter(3))
    mask+=(np.asarray(eroded)>0).astype(np.float32)/2
mask=np.minimum(mask,1)
Image.fromarray(np.round(mask*255).astype(np.uint8)).save(R/'interior-mask.png')
a=np.asarray(original).astype(np.float32);b=np.asarray(new).astype(np.float32)
out=np.round(a*(1-mask[:,:,None])+b*mask[:,:,None]).clip(0,255).astype(np.uint8)
assert np.array_equal(out[mask==0],np.asarray(original)[mask==0])
Image.fromarray(out).save(TARGET)
write(SIDECAR,{'schemaVersion':1,'file':str(TARGET),'sha256':sha(TARGET),'width':1254,'height':1254,'format':'PNG','role':'shared_geometry_with_AI_gray_face_artifact_cleanup','operation':'Native-scale AI fill composited only within two gray stone panels, 2px inward mask feather. No resize, warp or color correction. Pixels outside mask byte-equal.','derivedFrom':[{'file':old['derivedFrom'][0]['file'],'sha256':old['sha256'],'generationRecord':str(R/'before-source-record.json')},{'file':str(raw),'sha256':sha(raw),'generationRecord':str(raw)+'.generation.json'}],'mask':{'file':str(R/'interior-mask.png'),'sha256':sha(R/'interior-mask.png'),'polygons':polygons,'inwardFeatherPixels':2},'actualModel':None,'actualQuality':None,'qa':{'status':'pending_return_boundary_review','accepted':False},'sourceScale':1,'outsideMaskPixelEquality':True})
write(R/'processing.json',{'output':str(TARGET),'outputSha256':sha(TARGET),'sourceBeforeSha256':old['sha256'],'nativeGeneratedSha256':sha(raw),'resampling':None,'registration':None,'colorCorrection':None,'mask':str(R/'interior-mask.png'),'outsideMaskPixelEquality':True})
print(json.dumps({'output':str(TARGET),'sha256':sha(TARGET),'outsideMaskEqual':True}))

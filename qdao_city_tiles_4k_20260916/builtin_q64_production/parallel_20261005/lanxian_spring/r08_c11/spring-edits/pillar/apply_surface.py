from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageFilter
O=Path(__file__).resolve().parent;T=O.parents[1];R=Path('D:/work/image')
raw=Path('C:/Users/luyua/.codex/generated_images/01a10bb2-5cf3-7db0-a7f1-5c85ef972ed1/exec-c59a900a-b6a6-4ce1-9166-e853af545bb9.png')
source=T/'native/r01_c04.png'; style=R/'designs/gameplay-ui/04-guild.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with Image.open(source) as im: assert im.size==(1254,1254); a=np.array(im.convert('RGB'))
with Image.open(raw) as im: assert im.size==(1254,1254); b=np.array(im.convert('RGB'))
y,x=np.indices(a.shape[:2]);q=a.astype(np.int32);r,g,blue=q[:,:,0],q[:,:,1],q[:,:,2]
roi=(x>=960)&(x<1210)&(y<958)
mask=roi&(r-g>25)&(g-blue>10)&(r-blue>45)
alpha=mask.astype(np.uint8)*255
eroded=np.asarray(Image.fromarray(alpha).filter(ImageFilter.MinFilter(3)))>0
alpha[mask&~eroded]=176
z=alpha.astype(np.float32)[:,:,None]/255
result=np.rint(a.astype(np.float32)*(1-z)+b.astype(np.float32)*z).clip(0,255).astype(np.uint8)
assert np.array_equal(a[alpha==0],result[alpha==0])
ys,xs=np.where(alpha>0); bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
shutil.copyfile(raw,O/'ai-result1254.png');Image.fromarray(result).save(O/'edited-native1254.png');Image.fromarray(alpha).save(O/'alpha1254.png')
Image.fromarray(result).crop((925,0,1254,1020)).save(O/'pillar-and-protected-surroundings-1to1.png')
now=datetime.now(timezone.utc).isoformat()
write(O/'ai-result1254.png.generation.json',{'createdAtUtc':now,'generatedAtEvidence':read(O/'tool-result.json'),'sourceToolImage':info(raw),'file':str(O/'ai-result1254.png'),'sha256':sha(O/'ai-result1254.png'),'nativePixels':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(R/'config/image-generation.json'),'submittedParameters':{'prompt':(O/'prompt.txt').read_text(encoding='utf-8').strip(),'referenced_image_paths':[str(source),str(style)],'transparent_background':False,'model':None,'quality':None},'actualModel':None,'actualQuality':None,'references':[{**info(source),'role':'edit target, shared neutral native geometry'},{**info(style),'role':'confirmed painting/material style only'}]})
write(O/'processing.json',{'createdAtUtc':now,'source':info(source),'aiSource':info(O/'ai-result1254.png'),'output':info(O/'edited-native1254.png'),'alpha':info(O/'alpha1254.png'),'nativeSize':[1254,1254],'extendedPlacementXY':[3072,0],'sourceMaskBBox':bbox,'changedPixels':int(np.any(result!=a,axis=2).sum()),'maskOutsidePixelExact':True,'maskPolicy':'Restrict x960:1210,y0:958, original wood r-g>25,g-b>10,r-b>45; 1pixel inward alpha176, interior255. No geometry resampling.','operation':'AI lacquer pixels composited only on original pillar wood; all surroundings remain byte-equal','upscale':False,'warp':False,'imageBlur':False,'colorVariantOnly':True,'formalAccepted':False})
print(json.dumps({'bbox':bbox,'changedPixels':int(np.any(result!=a,axis=2).sum()),'outsideExact':True,'output':str(O/'edited-native1254.png')}))

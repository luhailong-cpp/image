from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,shutil
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");F=D/'final-v3';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
W=D/'wall-join-repair-v1';host=Path(r"C:/Users/luyua/.codex/generated_images/01a11b05-7488-7d11-bfe3-c3b64c8f7651/exec-92bf8981-6bed-49f6-983a-8aaa0de9b741.png");shutil.copy2(host,W/'native.png')
wp=json.loads((W/'preparation.json').read_text(encoding='utf-8'));(W/'native.png.generation.json').write_text(json.dumps({'output':ref(W/'native.png'),'host':ref(host),'preparation':ref(W/'preparation.json'),'configTarget':wp['configTarget'],'actualReturnedPixels':[1254,1254],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'nativeScale':1,'formalAccepted':False},indent=2),encoding='utf-8')
J=np.array(Image.open(D/'final-v2/joined.png').convert('RGB'));R=D/'coupled-whole-object-v1';N=np.array(Image.open(R/'native.png').convert('RGB'));C=np.array(Image.open(R/'source-composite.png').convert('RGBA'))
mask=np.array(Image.open(R/'mask.png').convert('L'));mask[420:1120,115:710]=255;Image.fromarray(mask).save(F/'lower-paint-mask.png')
m=np.maximum(np.array(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(5))).astype(float)/255,mask.astype(float)/255);m=np.where(C[:,:,3]==255,m,1);lower=np.rint(C[:,:,:3]*(1-m[:,:,None])+N*m[:,:,None]).astype(np.uint8);J[1024:]=lower
wall=np.array(Image.open(W/'native.png').convert('RGB'));y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1));w=smooth((x-970)/8)*(1-smooth((x-1192)/8))*(1-smooth((y-482)/8))
J[:1254]=np.rint(J[:1254]*(1-w[:,:,None])+wall*w[:,:,None]).astype(np.uint8);Image.fromarray(J).save(F/'joined.png');Image.fromarray(J[:1254]).save(F/'main1254.png');Image.fromarray(np.rint(w*255).astype(np.uint8)).save(F/'wall-repair-weight.png')
for name,box in [('main1254',[0,0,1254,1254]),('lower-native',[0,1024,1254,2278]),('middle-overlap',[0,700,1254,1500]),('right-upper',[920,0,1254,1200]),('right-lower',[900,1024,1254,2278]),('left-perimeter',[105,1139,260,2278]),('return-tail',[0,2050,1254,2278])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
asm=json.loads((D/'final-v2/assembly.json').read_text(encoding='utf-8'));asm.update({'output':ref(F/'joined.png'),'additionalAIWallSource':ref(W/'native.png'),'wallRepairWeight':ref(F/'wall-repair-weight.png'),'wallRepairLTRB':[970,0,1200,490],'lowerOwnershipMask':ref(F/'lower-paint-mask.png'),'leftGroundExtendedToBoundary':True,'reasonForOwnershipExtension':'Avoid a truncated old floor joint at x180 inside updated ground; repaint ownership extends to true tile boundary x115, adjacent unknown left tile not claimed.'})
(F/'assembly.json').write_text(json.dumps(asm,indent=2),encoding='utf-8');print(json.dumps(ref(F/'joined.png')))


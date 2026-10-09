from pathlib import Path
import json,hashlib,datetime,sys
from PIL import Image
import numpy as np
D=Path(sys.argv[1]);F=D/'final-v2';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True);ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'));y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1));side=read(D/'request.json')['knownSide'];cw=smooth((y-1040)/160)
if side=='right':cw=np.maximum(cw,smooth((x-1040)/160))
elif side=='left':cw=np.maximum(cw,smooth((214-x)/160))
cw=np.maximum(cw,smooth((y-1024)/24)*smooth((x-780)/50));cw=np.where(C[:,:,3]==255,cw,0);J=np.rint(N.astype(float)*(1-cw[:,:,None])+C[:,:,:3].astype(float)*cw[:,:,None]).astype('uint8');Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png')
boxes=[('bottom',[0,900,1254,1254]),('full-native',[0,0,1254,1254])]
if side:boxes += [(side,[0,0,354,1254] if side=='left' else [900,0,1254,1254]),('bottom-corner',[0,880,374,1254] if side=='left' else [880,880,1254,1254])]
for name,box in boxes:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'sourceWeight':ref(F/'source-weight.png'),'bottomSourceSmoothstepY':[1040,1200],'knownFoliageSourcePreference':{'xSmoothstep':[780,830],'ySmoothstep':[1024,1048],'reason':'Prefer exact original known leaf outlines to avoid soft duplicate leaves; no geometry or recoloring'},'sideSourceSmoothstep':{'side':side,'bounds':[54,214] if side=='left' else [1040,1200] if side else None},'contextExactBeyond1200':bool(np.array_equal(J[1200:],C[1200:,:,:3])),'unknownExactNative':bool(np.array_equal(J[C[:,:,3]==0],N[C[:,:,3]==0])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True});print(json.dumps(ref(F/'joined.png')))

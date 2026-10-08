from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;F=D/'final-v2';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));R=np.array(Image.open(D/'repair-v1/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
rw=smooth((y-850)/50);cw=smooth((y-1120)/80)
J=np.rint((N.astype(float)*(1-rw[:,:,None])+R.astype(float)*rw[:,:,None])*(1-cw[:,:,None])+C[:,:,:3].astype(float)*cw[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(rw*255).astype('uint8')).save(F/'repair-weight.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('bottom',[0,840,1254,1254]),('bottom-left',[0,920,700,1254]),('bottom-right',[600,920,1254,1254]),('repair-top',[0,800,1254,950]),('full-native',[0,0,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'repairNative':ref(D/'repair-v1/native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'repairWeight':ref(F/'repair-weight.png'),'sourceWeight':ref(F/'source-weight.png'),'repairSmoothstepY':[850,900],'sourceSmoothstepY':[1120,1200],'originalNativeExactAbove850':bool(np.array_equal(J[:850],N[:850])),'repairExactY900to1120':bool(np.array_equal(J[900:1120],R[900:1120])),'contextExactBeyond1200':bool(np.array_equal(J[1200:],C[1200:,:,:3])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True})
print(json.dumps(ref(F/'joined.png')))

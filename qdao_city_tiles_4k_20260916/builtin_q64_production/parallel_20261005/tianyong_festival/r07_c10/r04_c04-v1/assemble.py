from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;F=D/'final-v1';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254));t=np.clip((y-1040)/160,0,1);t=t*t*(3-2*t)
w=np.where(C[:,:,3]==255,t,0)
J=np.rint(N.astype(float)*(1-w[:,:,None])+C[:,:,:3].astype(float)*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png')
Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('bottom',[0,920,1139,1254]),('bottom-left',[0,960,600,1254]),('bottom-right',[540,960,1254,1254]),('full-native',[0,0,1254,1254])]:
 Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'blendSourceWeight':ref(F/'source-weight.png'),'blendSmoothstepRows':[1040,1200],'unknownPixelsUnchangedFromNative':bool(np.array_equal(J[C[:,:,3]==0],N[C[:,:,3]==0])),'contextExactAtAndBelowY1200':bool(np.array_equal(J[1200:,:1139],C[1200:,:1139,:3])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True})
print(json.dumps({'output':ref(F/'joined.png'),'newTilePixels':1139*1139,'returnBox':[2957,0,4096,61]},indent=2))

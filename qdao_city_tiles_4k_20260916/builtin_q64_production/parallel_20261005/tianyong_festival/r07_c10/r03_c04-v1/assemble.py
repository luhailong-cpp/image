from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;F=D/'final-v1';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'));y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
cw=np.where(C[:,:,3]==255,np.maximum(smooth((214-x)/160),smooth((y-1040)/160)),0);J=np.rint(N.astype(float)*(1-cw[:,:,None])+C[:,:,:3].astype(float)*cw[:,:,None]).astype('uint8');Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('bottom',[0,900,1254,1254]),('left',[0,0,354,1254]),('bottom-left',[0,720,600,1254]),('full-native',[0,0,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'sourceWeight':ref(F/'source-weight.png'),'bottomSourceSmoothstepY':[1040,1200],'leftSourceSmoothstepX':[54,214],'contextExactBeyond1200':bool(np.array_equal(J[1200:],C[1200:,:,:3])),'contextExactBefore54':bool(np.array_equal(J[:,:54],C[:,:54,:3])),'unknownExactNative':bool(np.array_equal(J[C[:,:,3]==0],N[C[:,:,3]==0])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True});print(json.dumps(ref(F/'joined.png')))

from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).parent;F=D/'final-v1';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));R=np.array(Image.open(D/'paving-repair-v1/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'));y,x=np.indices((1254,1254));s=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1));rw=s((690-y)/40);N2=np.rint(N*(1-rw[:,:,None])+R*rw[:,:,None]);cw=np.maximum(s((y-1040)/160),s((x-1040)/160));cw=np.where(C[:,:,3]==255,cw,0);J=np.rint(N2*(1-cw[:,:,None])+C[:,:,:3]*cw[:,:,None]).astype('uint8');Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png');Image.fromarray(np.rint(rw*255).astype('uint8')).save(F/'repair-weight.png')
for name,box in [('full-native',[0,0,1254,1254]),('repaired-floor',[0,0,1254,750]),('right',[900,0,1254,1254]),('bottom',[0,900,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'curbRepairNative':ref(D/'paving-repair-v1/native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'sourceWeight':ref(F/'source-weight.png'),'repairWeight':ref(F/'repair-weight.png'),'repairBlendY':[650,690],'bottomSourceSmoothstepY':[1040,1200],'sideSourceSmoothstepX':[1040,1200],'repairReason':'Remove generated diagonal fracture-like paving lines above balustrade with native AI repair.','actualModel':None,'actualQuality':None,'formalAccepted':False});print(json.dumps(ref(F/'joined.png')))



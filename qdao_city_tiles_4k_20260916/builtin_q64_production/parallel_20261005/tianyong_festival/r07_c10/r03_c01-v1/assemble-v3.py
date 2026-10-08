from pathlib import Path
import json,hashlib,datetime,sys
from PIL import Image
import numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent;F=D/'final-v3';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));R=np.array(Image.open(D/'repair-v1/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
rw=smooth((y-850)/50);cw=smooth((y-1120)/80)
B=np.rint(N.astype(float)*(1-rw[:,:,None])+R.astype(float)*rw[:,:,None]).astype('uint8')
controls=[[0,-2],[20,-2],[110,0],[140,0],[200,2],[230,2],[260,8],[440,8],[500,6],[530,11],[560,9],[590,8],[620,4],[680,4],[740,5],[800,6],[860,8],[920,0],[1253,0]]
dy=np.interp(x,np.array(controls)[:,0],np.array(controls)[:,1])*smooth((y-700)/350)
W=cv2.remap(B,x.astype('float32'),(y+dy).astype('float32'),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
J=np.rint(W.astype(float)*(1-cw[:,:,None])+C[:,:,:3].astype(float)*cw[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(rw*255).astype('uint8')).save(F/'repair-weight.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png');np.save(F/'inverse-dy.npy',dy)
for name,box in [('bottom',[0,840,1254,1254]),('bottom-left',[0,920,700,1254]),('bottom-right',[600,920,1254,1254]),('repair-top',[0,660,1254,950]),('full-native',[0,0,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'repairNative':ref(D/'repair-v1/native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':True,'registrationMethod':'Explicit measured per-column small inverse vertical displacement, interpolated controls with long smooth fade from zero above700 to full at1050; bicubic remap at unchanged pixel count. No global enlargement.','controls':controls,'maxDx':0,'maxDy':float(abs(dy).max()),'registrationField':ref(F/'inverse-dy.npy'),'registrationMeasurements':ref(D/'registration-measurements.json'),'toneCorrectionApplied':False,'repairWeight':ref(F/'repair-weight.png'),'sourceWeight':ref(F/'source-weight.png'),'repairSmoothstepY':[850,900],'sourceSmoothstepY':[1120,1200],'originalNativeExactAbove700':bool(np.array_equal(J[:700],N[:700])),'contextExactBeyond1200':bool(np.array_equal(J[1200:],C[1200:,:,:3])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True})
print(json.dumps(ref(F/'joined.png')))

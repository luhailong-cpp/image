from pathlib import Path
import json,hashlib,datetime,sys
from PIL import Image
import numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent;F=D/'final-v1';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()};save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));R=np.array(Image.open(D/'repair-v2/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'));M=np.array(Image.open(D/'repair-v2/edit-mask.png'))>0
M[1100:,:700]=True
y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
distance=cv2.distanceTransform((~M).astype('uint8'),cv2.DIST_L2,5);rw=1-smooth(distance/35)
B=N.astype(float)*(1-rw[:,:,None])+R.astype(float)*rw[:,:,None]
special=smooth((y-720)/60)*(1-smooth((y-1120)/40));wl=smooth((214-x)/160)*(1-special)+smooth((16-x)/16)*special
wb=smooth((y-1120)/80);cw=np.where(C[:,:,3]==255,np.maximum(wl,wb),0)
J=np.rint(B*(1-cw[:,:,None])+C[:,:,:3].astype(float)*cw[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(rw*255).astype('uint8')).save(F/'repair-weight.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('bottom',[0,900,1254,1254]),('left',[0,0,354,1254]),('bottom-left',[0,720,600,1254]),('repair-diagonal',[0,700,550,1254]),('full-native',[0,0,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'repairNative':ref(D/'repair-v2/native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'repairWeight':ref(F/'repair-weight.png'),'sourceWeight':ref(F/'source-weight.png'),'repairMask':ref(D/'repair-v2/edit-mask.png'),'repairMaskOutwardFeather':35,'bottomSourceSmoothstepY':[1120,1200],'normalLeftSourceSmoothstepX':[54,214],'repairedLeftSourceSmoothstepX':[0,16],'repairedLeftFullY':[780,1120],'contextExactBeyond1200':bool(np.array_equal(J[1200:],C[1200:,:,:3])),'contextExactAtLeftEdge':bool(np.array_equal(J[:,0],C[:,0,:3])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True})
print(json.dumps(ref(F/'joined.png')))

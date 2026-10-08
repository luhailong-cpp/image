from pathlib import Path
import json,hashlib,datetime,sys
from PIL import Image
import numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent;F=D/'final-v1';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
N=np.array(Image.open(D/'native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
assert N.shape==(1254,1254,3)
y,x=np.indices((1254,1254));dist=np.maximum(x,y);t=np.clip((dist-1040)/160,0,1);t=t*t*(3-2*t)
w=np.where(C[:,:,3]==255,t,0)
J=np.rint(N.astype(float)*(1-w[:,:,None])+C[:,:,:3].astype(float)*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('bottom',[0,920,1254,1254]),('right',[920,0,1254,1254]),('bottom-right',[880,880,1254,1254]),('full-native',[0,0,1254,1254])]:
 Image.fromarray(J).crop(box).save(Q/(name+'.png'))
c=cv2.cvtColor(C[:,:,:3],cv2.COLOR_RGB2GRAY).astype(float);n=cv2.cvtColor(N,cv2.COLOR_RGB2GRAY).astype(float)
cg=np.gradient(c,axis=0);ng=np.gradient(n,axis=0)
measures=[]
for xx in [1040,1070,1100,1130,1160,1190,1220,1240]:
 for lo,hi in [(0,300),(300,600),(650,950),(950,1254)]:
  start=lo+10;end=hi-10;g=cg[start:end,xx-4:xx+5]
  if np.max(abs(g))<1.5:continue
  scores=[np.mean(abs(g-ng[start+s:end+s,xx-4:xx+5])) for s in range(-10,11)]
  measures.append({'x':xx,'yRange':[start,end],'inverseDy':int(np.argmin(scores))-10,'score':float(min(scores)),'scoreAtZero':float(scores[10])})
save(F/'right-measurements.json',{'controls':measures})
save(F/'assembly.json',{'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'blendSourceWeight':ref(F/'source-weight.png'),'blendSmoothstepMaxXY':[1040,1200],'unknownPixelsUnchangedFromNative':bool(np.array_equal(J[C[:,:,3]==0],N[C[:,:,3]==0])),'contextExactBeyond1200':bool(np.array_equal(J[dist>=1200],C[:,:,:3][dist>=1200])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'rootCommitRequired':True})
print(json.dumps({'joined':ref(F/'joined.png'),'rightMeasures':measures},indent=2))

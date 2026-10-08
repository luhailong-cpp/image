from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
D=Path(__file__).parent;F=D/(sys.argv[2] if len(sys.argv)>2 else 'final-v1');F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
native_path=D/(sys.argv[1] if len(sys.argv)>1 else 'repair-v1/native.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
N=np.array(Image.open(native_path).convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254));smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
w=np.where(C[:,:,3]==255,np.maximum(smooth((x-1040)/160),smooth((y-1139)/61)),0)
J=np.rint(N*(1-w[:,:,None])+C[:,:,:3]*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('right',[944,0,1254,1254]),('bottom',[0,1040,1254,1254]),('corner',[900,950,1254,1254]),('full',[0,0,1254,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
grey=lambda a:a[:,:,:3].astype(float).mean(axis=2)
cg=grey(C);ng=grey(N);gxC=np.gradient(cg,axis=1);gxN=np.gradient(ng,axis=1);gyC=np.gradient(cg,axis=0);gyN=np.gradient(ng,axis=0)
controls=[]
for yy in (1150,1180,1210,1230):
 for lo,hi in ((5,260),(450,740),(750,1020),(1000,1235)):
  if abs(gxC[yy,lo:hi]).max()<2:continue
  lo=max(lo,22);hi=min(hi,1232)
  scores=[float(np.mean(abs(gxC[yy-3:yy+4,lo:hi]-gxN[yy-3:yy+4,lo+s:hi+s]))) for s in range(-12,13)]
  controls.append({'edge':'bottom','y':yy,'xRange':[lo,hi],'inverseDx':int(np.argmin(scores))-12,'scoreAtZero':scores[12],'bestScore':min(scores)})
for xx in (1050,1100,1150,1190,1220):
 for lo,hi in ((22,300),(300,700),(700,1040),(1000,1232)):
  if abs(gyC[lo:hi,xx]).max()<2:continue
  scores=[float(np.mean(abs(gyC[lo:hi,xx-3:xx+4]-gyN[lo+s:hi+s,xx-3:xx+4]))) for s in range(-12,13)]
  controls.append({'edge':'right','x':xx,'yRange':[lo,hi],'inverseDy':int(np.argmin(scores))-12,'scoreAtZero':scores[12],'bestScore':min(scores)})
save(F/'measurements.json',{'method':'signed grayscale derivative profile comparison in authentic known overlap; diagnostic only','controls':controls,'noRegistrationApplied':True})
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(native_path),'context':ref(D/'context.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'sourceWeight':ref(F/'source-weight.png'),'blendSmoothstepX':[1040,1200],'blendSmoothstepY':[1139,1200],'unknownPixelsUnchangedFromNative':bool(np.array_equal(J[C[:,:,3]==0],N[C[:,:,3]==0])),'knownAtX1200OrY1200Exact':bool(np.array_equal(J[(C[:,:,3]==255)&((x>=1200)|(y>=1200))],C[:,:,:3][(C[:,:,3]==255)&((x>=1200)|(y>=1200))])),'formalAccepted':False,'visualReviewPending':True})
print(json.dumps({'output':ref(F/'joined.png'),'controls':controls},indent=2))

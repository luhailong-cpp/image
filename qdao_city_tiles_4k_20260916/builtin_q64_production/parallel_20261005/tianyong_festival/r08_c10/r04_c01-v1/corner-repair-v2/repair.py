from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
O=Path(__file__).resolve().parent;P=O.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def png(n,a):Image.fromarray(np.rint(a).clip(0,255).astype('uint8')).save(O/n)
def ss(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
base=np.asarray(Image.open(P/'final-v2/r04_c01-joined.png').convert('RGB'),np.float32);ai=np.asarray(Image.open(P/'left-repair-v1/native.png').convert('RGB'),np.float32)
ctx=np.asarray(Image.open(P/'repaired-v1/original-context.png').convert('RGB'),np.float32);lum=lambda a:a@np.array([.2126,.7152,.0722]);bl=lum(base);al=lum(ai);cl=lum(ctx)
def end(a,y,lo,hi):
 # Subpixel outer edge at luminance250, same physical highlight on both candidates.
 xs=np.flatnonzero(a[y,lo:hi]>=250)+lo;e=int(xs[-1]);return e+(250-a[y,e])/(a[y,e+1]-a[y,e])
ys=[850,860,870,880,920,924,928,932];target=[]
for y in ys:target.append(end(bl if y<900 else cl,y,60,150 if y<900 else 115))
pt=np.polynomial.polynomial.polyfit((np.asarray(ys)-900)/40,target,2)
fitrows=np.arange(850,931);aiedges=[end(al,int(y),40,150) for y in fitrows];pa=np.polynomial.polynomial.polyfit((fitrows-900)/40,aiedges,2)
xx,yy=np.meshgrid(np.arange(1254,dtype=np.float32),np.arange(1254,dtype=np.float32))
def monotone_curve(qx,qy,xx):
 qx=np.asarray(qx,float);qy=np.asarray(qy,float);h=np.diff(qx);s=np.diff(qy)/h;m=np.zeros(len(qx));m[0]=s[0];m[-1]=s[-1]
 for k in range(1,len(qx)-1):
  if s[k-1]*s[k]>0:
   w1=2*h[k]+h[k-1];w2=h[k]+2*h[k-1];m[k]=(w1+w2)/(w1/s[k-1]+w2/s[k])
 ids=np.clip(np.searchsorted(qx,xx)-1,0,len(qx)-2);t=np.clip((xx-qx[ids])/h[ids],0,1)
 return (2*t**3-3*t*t+1)*qy[ids]+(t**3-2*t*t+t)*h[ids]*m[ids]+(-2*t**3+3*t*t)*qy[ids+1]+(t**3-t*t)*h[ids]*m[ids+1]
tx=monotone_curve(ys,target,np.arange(1254))
smoothed_ai=cv2.GaussianBlur(np.asarray(aiedges,np.float32)[:,None],(1,0),1.25).ravel()
ax=np.interp(np.arange(1254),fitrows,smoothed_ai)
dx=np.clip(ax-tx,-24,24).astype('float32');source=cv2.remap(ai,xx+dx[:,None],yy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
alpha=ss((yy-855)/25)*(1-ss((yy-915)/18))*ss((xx-(tx[:,None]-22))/10)*(1-ss((xx-(tx[:,None]+9))/11))
out=base*(1-alpha[:,:,None])+source*alpha[:,:,None];out=np.rint(out).clip(0,255).astype('uint8');png('joined.png',out);png('qa-corner.png',out[820:970,45:245]);png('qa-before-beside-after.png',np.concatenate([base[860:950,80:165],out[860:950,80:165]],1));png('mask.png',alpha*255)
np.save(O/'alpha.npy',alpha);np.save(O/'source-dx.npy',dx)
ol=lum(out);track=[]
for x in range(108,123):
 v=np.flatnonzero(ol[880:940,x]>=250);track.append({'x':x,'lastBrightY':int(v[-1])+880 if len(v) else None})
write('parameters.json',{'base':info(P/'final-v2/r04_c01-joined.png'),'aiSource':info(P/'left-repair-v1/native.png'),'selection':'AI redraw of existing left outer highlight only, aligned to retained upper/genuine lower visible endpoints; no procedural line drawing','targetFitRows':ys,'targetX':target,'targetInterpolator':'Monotone C1 Hermite through measured native anchors','aiEdgeEstimator':'Per-row measured luminance250 edge, Gaussian1.25 vertical smoothing','maxInverseDxWithinSelectedPixels':float(np.abs(np.broadcast_to(dx[:,None],alpha.shape)[alpha>0]).max()),'verticalDisplacement':0,'toneApplied':False,'alpha':info(O/'alpha.npy'),'sourceDx':info(O/'source-dx.npy'),'track':track,'nativeSize':[1254,1254],'formalAccepted':False,'pendingVisualReview':True})
print(json.dumps({'joined':info(O/'joined.png'),'track':track,'target':target}))

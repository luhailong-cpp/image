from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
O=P/'registration-v1';O.mkdir(exist_ok=True)
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def png(n,a): Image.fromarray(np.rint(a).clip(0,255).astype('uint8')).save(O/n)
smooth=lambda a:np.clip(a,0,1)**2*(3-2*np.clip(a,0,1))
raw=np.array(Image.open(P/'native.png').convert('RGB'))
ctx=np.array(Image.open(P/'original-context.png').convert('RGBA'))
assert raw.shape==(1254,1254,3)
known=ctx[:,:,3]==255; source=ctx[:,:,:3]
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# Measured signed horizontal source sampling correction at the two lower curved bevels.
# No optical-flow inference, vertical displacement or scaling.
dx=np.interp(xx,[0,440,470,638,1024,1139,1253],[0,0,0,-2,-1,0,0]).astype(np.float32)*smooth((yy-800)/224)
aligned=cv2.remap(raw,xx+dx,yy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
distance=cv2.distanceTransform((~known).astype(np.uint8),cv2.DIST_L2,5)
delta=source.astype(np.float32)-aligned.astype(np.float32);delta[~known]=0
norm=cv2.GaussianBlur(known.astype(np.float32),(0,0),24)
tone=cv2.GaussianBlur(delta,(0,0),24)/np.maximum(norm[:,:,None],.0001)
tone=np.clip(tone,-12,12)*(1-smooth(distance/160))[:,:,None]
corrected=np.clip(aligned.astype(np.float32)+tone,0,255)
# Exactly preserve the exterior 12 pixels and taper only across real native overlap.
alpha=smooth((xx-12)/103)*smooth((1226-xx)/202)*smooth((1226-yy)/202)*smooth((yy-12)/80)
alpha[~known]=1
joined=np.rint(corrected*alpha[:,:,None]+source.astype(np.float32)*(1-alpha[:,:,None])).clip(0,255).astype(np.uint8)
assert np.array_equal(joined[:,:12],source[:,:12])
assert np.array_equal(joined[:,1226:],source[:,1226:])
assert np.array_equal(joined[1226:],source[1226:])
assert np.array_equal(joined[:12][known[:12]],source[:12][known[:12]])
png('joined.png',joined);png('mask.png',alpha*255);np.save(O/'dx.npy',dx);np.save(O/'tone.npy',tone)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'nativeScale':1,'output':info(O/'joined.png'),'derivedFrom':[info(P/'native.png'),info(P/'original-context.png')],'operation':'Native 1:1 return blending after explicit horizontal registration max 2px and capped local RGB correction max12. No guide pixels, new generation or enlargement.','maxDx':float(np.max(np.abs(dx))),'maxDy':0,'maxToneRGB':np.abs(tone).max((0,1)).tolist(),'outsideLeft12Right28Bottom28Exact':True,'script':info(Path(__file__)),'fields':[info(O/x) for x in ['mask.png','dx.npy','tone.npy']],'formalAccepted':False}
save('assembly.json',record)
save('joined.png.generation.json',{**info(O/'joined.png'),'derivedFrom':record['derivedFrom'],'assembly':info(O/'assembly.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'operation':record['operation']})
qa=[('left-return.png',[0,0,300,1254]),('right-return.png',[924,0,1254,1254]),('bottom-return.png',[0,900,1254,1254]),('corner-left.png',[0,900,350,1254]),('corner-right.png',[904,900,1254,1254])]
for n,b in qa:
 Image.fromarray(joined).crop(b).save(O/n)
 save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(O/'joined.png')],'operation':'Exact native crop for visual inspection','cropLTRB':b,'newModelCalls':0})
print(json.dumps(record))

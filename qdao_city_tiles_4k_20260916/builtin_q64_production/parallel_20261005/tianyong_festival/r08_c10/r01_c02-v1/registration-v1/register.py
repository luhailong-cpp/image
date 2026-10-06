"""Small deterministic contour registration of an already complete native patch.

No AI pixels are synthesized here. The right native context owns x>=1104.
"""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent; D=P.parent
ROOT=next(p for p in D.parents if (p/'config/image-generation.json').exists())
sys.path.insert(0,str(ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor'))
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
smo=lambda v:np.clip(v,0,1)**2*(3-2*np.clip(v,0,1))
n=np.array(Image.open(D/'native.png').convert('RGB'))
c=np.array(Image.open(D/'context.png').convert('RGBA'))
assert n.shape==(1254,1254,3) and np.all(c[:,1024:,3]==255) and not c[:,:1024,3].any()
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# The right crossing corner matched at inverse(-6,+4) with NCC0.988.
# Use that identifiable2D corner. Long straight edges use horizontal-only
# matching to avoid along-edge aperture drift. Approach spans404 pixels.
yc=np.array([0,380,460,550,620,680,720,790,860,940,1000,1040,1090,1140,1200,1253])
dxv=np.array([0,0,0,-2,-5.5,-6,-5.5,-5,-4,-3,-3,-3,-7.2,-7.5,-6.3,-5.5])
dxp=np.interp(np.arange(1254),yc,dxv).astype(np.float32)
dxp=cv2.GaussianBlur(dxp[:,None],(1,0),sigmaX=0,sigmaY=16)[:,0]
xramp=smo((xx-620)/404)
dx=dxp[:,None]*xramp
# The upper shallow diagonal seam needs only a1px vertical correction.
# Main corner requires4px, with broad y taper preserving its tangent.
dyp=np.interp(np.arange(1254),[0,200,250,330,380,480,550,630,705,800,860,1253],[0,0,-1,-1,0,0,1,4,4,0,0,0]).astype(np.float32)
dyp=cv2.GaussianBlur(dyp[:,None],(1,0),sigmaX=0,sigmaY=16)[:,0]
dy=dyp[:,None]*xramp
flow=np.stack([dx,dy],axis=2).astype(np.float32)
aligned=cv2.remap(n,xx+dx,yy+dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
known=(c[:,:,3]==255)
delta=c[:,:,:3].astype(np.float32)-aligned.astype(np.float32);delta[~known]=0
norm=cv2.GaussianBlur(known.astype(np.float32),(0,0),20)
tone=cv2.GaussianBlur(delta,(0,0),20)/np.maximum(norm[:,:,None],.001)
# Extend the smooth observed correction into the new field, tapering over364px.
tone[:,:1024]=tone[:,1024:1025]
tone=np.clip(tone,-12,12)*xramp[:,:,None]
corrected=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
alpha=1-smo((xx-1024)/80)
joined=np.rint(corrected*alpha[:,:,None]+c[:,:,:3]*(1-alpha[:,:,None])).clip(0,255).astype(np.uint8)
assert np.array_equal(joined[:,1104:],c[:,1104:,:3])
assert np.array_equal(joined[:,:620],n[:,:620])
Image.fromarray(joined).save(P/'joined.png')
Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(P/'mask.png')
np.save(P/'flow.npy',flow);np.save(P/'tone.npy',tone)
qa=[]
for name,box in [('right-return-474x1254',(780,0,1254,1254)),('upper-return',(780,150,1254,410)),('lower-rim-return',(780,870,1254,1130)),('lower-joint-return',(730,540,1254,830)),('bottom-return',(700,1040,1254,1254))]:
 q=P/(name+'.png');Image.fromarray(joined).crop(box).save(q);qa.append({**ref(q),'cropLTRB':list(box),'sourceSha256':sha(P/'joined.png'),'operation':'1:1 crop; no resampling'})
 # Native / context / final side by side, 1:1.
 w,h=box[2]-box[0],box[3]-box[1];board=Image.new('RGB',(w*3,h))
 for i,im in enumerate([Image.fromarray(n),Image.fromarray(c).convert('RGB'),Image.fromarray(joined)]):board.paste(im.crop(box),(i*w,0))
 if name!='right-return-474x1254':board.save(P/(name+'-comparison.png'))
metrics=[]
ng=n.mean(2);cg=c[:,:,:3].mean(2);jg=joined.mean(2)
for label,base,slope,xs in [('upper',311,-.332,[1025,1041,1057,1073,1105,1137,1169,1201,1233]),('lower',698,-.335,[1065,1081,1097,1113,1145,1177,1209,1241])]:
 for x in xs:
  y0=round(base+(x-1065)*slope) if label=='lower' else round(base+(x-1024)*slope)
  vals=[]
  for arr in [ng,cg,jg]:
   prof=arr[y0-12:y0+13,x-1:x+2].mean(1);vals.append(y0-12+int(prof.argmin()))
  metrics.append({'feature':label,'x':x,'nativeY':vals[0],'contextY':vals[1],'joinedY':vals[2],'residual':vals[2]-vals[1]})
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Native-size contour-controlled inverse registration and local tone matching; source-preserving overlap; no new model generation; no upscale or guide pixels.','source':[ref(D/'native.png'),ref(D/'context.png')],'originalGenerationRecord':ref(D/'native.png.generation.json'),'output':ref(P/'joined.png'),'globalLTRB':[37773,28557,39027,29811],'tileLocalLTRB':[909,-115,2163,1139],'nativePixels':[1254,1254],'maximumAllowedShiftXY':[8,5],'actualMaxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),'maxAdjacentFieldChangeXY':np.abs(np.diff(flow,axis=1)).max(axis=(0,1)).tolist(),'maximumAllowedTone':12,'actualToneMaxRGB':np.abs(tone).max(axis=(0,1)).tolist(),'knownContextUnchangedXFrom':1104,'unmodifiedNativeXBefore':620,'resampling':'OpenCV INTER_CUBIC, same1254x1254 dimensions, BORDER_REPLICATE','fields':[ref(P/z) for z in ['flow.npy','tone.npy','mask.png']],'script':ref(Path(__file__)),'measuredLowerJoint':metrics,'qa':qa,'newModelCalls':0,'actualModel':None,'actualQuality':None,'unverifiedReason':'Derived from saved builtin native outputs. Actual model and quality are undisclosed; see original records.','accepted':False,'formalAccepted':False}
(P/'assembly.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
(P/'joined.png.generation.json').write_text(json.dumps({'file':str(P/'joined.png'),'sha256':sha(P/'joined.png'),'derivedFrom':record['source'],'operation':record['operation'],'assembly':ref(P/'assembly.json'),'nativePixels':[1254,1254],'exportPixels':[1254,1254],'newModelCalls':0,'actualModel':None,'actualQuality':None},indent=2)+'\n')
(P/'qa-crops.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps({'output':record['output'],'maxShift':record['actualMaxShiftXY'],'tone':record['actualToneMaxRGB'],'lowerJoint':metrics},indent=2))

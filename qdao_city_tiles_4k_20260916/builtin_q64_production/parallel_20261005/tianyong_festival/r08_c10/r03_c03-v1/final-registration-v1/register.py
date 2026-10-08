from pathlib import Path
from PIL import Image
import numpy as np,sys,json,hashlib
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent.parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(t):
 t=np.clip(t,0,1);return t*t*(3-2*t)
raw=np.array(Image.open(P/'r03_c03-repair-v1/native.png').convert('RGB'))
base=np.array(Image.open(P/'registration-v3/joined.png').convert('RGB'))
checkpoint=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
assert checkpoint['version']=='v010'
source=checkpoint['fragment'];assert sha(source['file'])==source['sha256']
ctx=np.array(Image.open(source['file']).convert('RGBA').crop((1933,1933,3187,3187)))
known=ctx[:,:,3]==255
y,x=np.mgrid[:1254,:1254].astype(np.float32)
# The AI repair carries complete crossband bevels. Align secondary existing
# horizontal contours by <=3px at the right insertion return.
flow=np.zeros((1254,1254,2),np.float32)
dy_y=np.interp(y[:,0],[0,640,674,689,730,783,793,819,850,900,1253],[0,0,-1,0,0,0,-3,-3,0,0,0])
flow[:,:,1]=dy_y[:,None]*smooth((x-250)/180)
flow[:,:,0]=smooth((y-840)/80)*(1-smooth((y-920)/100))*np.exp(-((x-270)/45)**2)
align=cv2.remap(raw,x+flow[:,:,0],y+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
target=base.copy();target[known]=ctx[:,:,:3][known]
# Estimate texture-only bounded RGB correction on corresponding boundary faces.
# The correction does not spread or remove geometric edges.
gray=target.astype(float).mean(2);gray2=align.astype(float).mean(2)
flat=(np.hypot(*np.gradient(gray))<4)&(np.hypot(*np.gradient(gray2))<4)
support=((x>=470)&(x<510)&(y>=500)&(y<960))|((x>=210)&(x<470)&(((y>=500)&(y<540))|((y>=920)&(y<960))))|((x>=190)&(x<230)&(y>=500)&(y<960))
support&=flat
delta=np.clip(target.astype(np.float32)-align.astype(np.float32),-12,12)
den=cv2.GaussianBlur(support.astype(np.float32),(0,0),20)
num=cv2.GaussianBlur(delta*support[:,:,None],(0,0),20)
tone=np.clip(num/np.maximum(den[:,:,None],1e-5),-12,12)
tone*=np.minimum(den[:,:,None]/0.002,1)
corrected=np.clip(np.rint(align.astype(np.float32)+tone),0,255).astype(np.uint8)
# A narrow16px texture transition is only applied after existing contours align.
w=smooth((x-222)/8)*(1-smooth((x-454)/32))*smooth((y-524)/32)*(1-smooth((y-904)/32))
joined=np.rint(base*(1-w[:,:,None])+corrected*w[:,:,None]).astype(np.uint8)
# Current c02 upper strip has an11px higher top crossband.
# A local inverse y displacement joins that existing contour, tapering gradually
# to no change by x500 and y200. No new structure supplied by this field.
topflow=np.zeros((1254,1254,2),np.float32)
topflow[:,:,1]=11*(1-smooth((x-230)/270))*(1-smooth((y-100)/100))
talign=cv2.remap(joined,x+topflow[:,:,0],y+topflow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# Surface matching at newest left context, applied in missing pixels only.
leftdelta=np.clip(ctx[:,:230,:3].astype(float)-talign[:,:230].astype(float),-12,12)
lf=np.hypot(*np.gradient(ctx[:,:230,:3].astype(float).mean(2)))<4
lfg=np.hypot(*np.gradient(talign[:,:230].astype(float).mean(2)))<4
valid=lf&lfg&(np.arange(230)[None,:]>=200)
profile=(leftdelta*valid[:,:,None]).sum(1)/np.maximum(valid.sum(1)[:,None],1)
profile=cv2.GaussianBlur(profile[:,None,:].astype(np.float32),(0,0),sigmaX=1,sigmaY=12)[:,0]
ltone=np.clip(profile[:,None,:],-12,12)*(1-smooth((x-230)/130))[:,:,None]*(1-smooth((y-460)/120))[:,:,None]
joined=np.clip(np.rint(talign.astype(float)+ltone),0,255).astype(np.uint8)
joined[known]=ctx[:,:,:3][known]
Image.fromarray(joined).save(O/'joined.png')
np.save(O/'repair-field.npy',flow);np.save(O/'top-field.npy',topflow);np.save(O/'repair-tone.npy',tone);np.save(O/'left-tone.npy',ltone)
Image.fromarray((w*255).astype(np.uint8)).save(O/'repair-mask.png')
Image.fromarray(ctx).save(O/'context.png')
qa=O/'qa';qa.mkdir(exist_ok=True)
rois={'whole':(0,0,1254,1254),'left':(130,0,360,1254),'upper-left':(130,0,570,270),'repair-surround':(130,440,570,1020),'repair-top':(190,480,530,620),'repair-bottom':(190,860,530,990),'repair-right':(390,540,550,950),'bottom':(0,900,1254,1254),'right':(900,0,1254,1254)}
for name,roi in rois.items():Image.fromarray(joined).crop(roi).save(qa/(name+'.png'))
write(O/'assembly.json',{'operation':'Native repair stitching; structure-correspondent bounded local inverse sampling and <=12 RGB matching. No new AI and no scale change.','sourceFiles':[info(P/'registration-v3/joined.png'),info(P/'r03_c03-repair-v1/native.png'),source],'checkpoint':info(T/'source-checkpoint.json'),'image':info(O/'joined.png'),'nativeScale':1,'dimensions':[1254,1254],'repairFieldMax':np.abs(flow).max((0,1)).tolist(),'topFieldMax':np.abs(topflow).max((0,1)).tolist(),'toneMax':float(max(abs(tone).max(),abs(ltone).max())),'fixedContextExact':bool(np.array_equal(joined[known],ctx[:,:,:3][known])),'repairBlendWidthPx':32,'repairBlendPurpose':'Texture transition after <=3px corresponding contour alignment, never missing structure concealment','resampling':'OpenCV bicubic remap, unchanged1254x1254 canvas','script':info(Path(__file__)),'localAccepted':False})
write(O/'qa/manifest.json',[{**info(qa/(n+'.png')),'cropFromJoinedLTRB':list(b),'nativeScale':1} for n,b in rois.items()])
print(json.dumps({'image':info(O/'joined.png'),'fixedContextExact':bool(np.array_equal(joined[known],ctx[:,:,:3][known]))}))


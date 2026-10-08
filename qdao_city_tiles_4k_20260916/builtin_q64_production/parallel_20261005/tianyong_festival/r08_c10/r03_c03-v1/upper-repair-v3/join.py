from pathlib import Path
from PIL import Image
import numpy as np,sys,json,hashlib
O=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
raw=np.array(Image.open(O/'native.png').convert('RGB'));base=np.array(Image.open(O.parent/'final-registration-v1/joined.png').convert('RGB'))
y,x=np.mgrid[:1254,:1254].astype(np.float32)
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
flow=np.zeros((1254,1254,2),np.float32)
# Match the already present gray inset upper edge at right; preserve ivory slab above.
wy=np.where(y<=84,smooth((y-59)/25),1-smooth((y-84)/116))
flow[:,:,1]=-13*smooth((x-230)/200)*wy
# AI's lower vertical left gray highlight is2px right of the original at y240.
flow[:,:,0]=2*smooth((y-160)/80)*(1-smooth((y-240)/40))*np.exp(-((x-251)/25)**2)
aligned=cv2.remap(raw,x+flow[:,:,0],y+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# Keep original upright separators above y60, outside the narrow left return.
w=(1-smooth((x-410)/32))*(1-smooth((y-228)/32))*(x>=230)
w*=np.maximum(1-smooth((x-295)/20),smooth((y-60)/8))
# Estimate bounded face correction from surrounding original pixels.
gray=base.astype(float).mean(2);g2=aligned.astype(float).mean(2)
flat=(np.hypot(*np.gradient(gray))<4)&(np.hypot(*np.gradient(g2))<4)
support=(((x>=410)&(x<450)&(y>=80)&(y<280))|((y>=240)&(y<280)&(x>=220)&(x<430))|((x>=190)&(x<230)&(y<240)))&flat
delta=np.clip(base.astype(np.float32)-aligned.astype(np.float32),-12,12)
den=cv2.GaussianBlur(support.astype(np.float32),(0,0),12);num=cv2.GaussianBlur(delta*support[:,:,None],(0,0),12)
tone=np.clip(num/np.maximum(den[:,:,None],1e-5),-12,12)*np.minimum(den[:,:,None]/.002,1)
corrected=np.clip(np.rint(aligned.astype(float)+tone),0,255)
joined=np.rint(base*(1-w[:,:,None])+corrected*w[:,:,None]).astype(np.uint8)
Image.fromarray(joined).save(O/'joined-candidate.png')
for n,b in [('upper',(180,0,510,330)),('whole',(0,0,1254,1254))]:Image.fromarray(joined).crop(b).save(O/(n+'-candidate.png'))
np.save(O/'field.npy',flow);np.save(O/'tone.npy',tone);Image.fromarray((w*255).astype(np.uint8)).save(O/'mask.png')


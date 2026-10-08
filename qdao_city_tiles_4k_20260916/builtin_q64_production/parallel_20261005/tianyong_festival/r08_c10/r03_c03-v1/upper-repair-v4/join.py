from pathlib import Path
from PIL import Image
import numpy as np,sys,json,hashlib
O=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
n=np.array(Image.open(O/'native.png').convert('RGB'));b=np.array(Image.open(O.parent/'final-registration-v1/joined.png').convert('RGB'))
y,x=np.mgrid[:1254,:1254].astype(np.float32)
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
f=np.zeros((1254,1254,2),np.float32)
dx=np.interp(y[:,0],[0,80,140,180,220,260,280,300,320,380,1253],[0,0,3,5,6.5,5.5,4.5,4.5,3,0,0])
f[:,:,0]=dx[:,None]*(1-smooth((x-265)/50))
dy=np.interp(y[:,0],[0,35,49,64,81,120,1253],[0,0,2,-1,0,0,0])
f[:,:,1]=dy[:,None]*smooth((x-230)/70)
a=cv2.remap(n,x+f[:,:,0],y+f[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
gray=b.astype(float).mean(2);g2=a.astype(float).mean(2)
flat=(np.hypot(*np.gradient(gray))<4)&(np.hypot(*np.gradient(g2))<4)
support=(((x>=290)&(x<320)&(y<330))|((y>=290)&(y<320)&(x>=210)&(x<320))|((x>=210)&(x<230)&(y<330)))&flat
delta=np.clip(b.astype(np.float32)-a.astype(np.float32),-12,12)
den=cv2.GaussianBlur(support.astype(np.float32),(0,0),10);num=cv2.GaussianBlur(delta*support[:,:,None],(0,0),10)
tone=np.clip(num/np.maximum(den[:,:,None],1e-6),-12,12)*np.minimum(den[:,:,None]/.002,1)
a=np.clip(np.rint(a.astype(float)+tone),0,255)
w=(x>=230)*(1-smooth((x-286)/28))*(1-smooth((y-286)/28))
j=np.rint(b*(1-w[:,:,None])+a*w[:,:,None]).astype(np.uint8)
Image.fromarray(j).save(O/'joined.png')
np.save(O/'field.npy',f);np.save(O/'tone.npy',tone);Image.fromarray((w*255).astype(np.uint8)).save(O/'mask.png')
qa=O/'qa';qa.mkdir(exist_ok=True)
rs={'whole':(0,0,1254,1254),'left':(130,0,370,1254),'upper-left':(170,0,450,380),'repair-top':(130,440,570,640),'repair-bottom':(130,840,570,1020),'repair-right':(390,540,570,970),'crossband':(0,600,700,870),'bottom':(0,900,1254,1254),'right':(900,0,1254,1254),'corner-bottom-left':(130,930,430,1150),'corner-bottom-right':(910,900,1200,1150)}
for name,box in rs.items():Image.fromarray(j).crop(box).save(qa/(name+'.png'))
(O/'qa/regions.json').write_text(json.dumps(rs,indent=2),encoding='utf-8')


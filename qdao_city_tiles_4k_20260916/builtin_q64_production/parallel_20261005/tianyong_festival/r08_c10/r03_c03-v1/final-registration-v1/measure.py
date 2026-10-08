from pathlib import Path
from PIL import Image
import numpy as np,sys,json
O=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
raw=np.array(Image.open(O.parent/'r03_c03-repair-v1/native.png').convert('RGB'))
base=np.array(Image.open(O.parent/'registration-v3/joined.png').convert('RGB'))
ctx=np.array(Image.open(O/'context.png').convert('RGBA'))
# Edge traces near correction rectangle; known latest target for left and old accepted geometry elsewhere.
target=base.copy();target[ctx[:,:,3]==255]=ctx[:,:,:3][ctx[:,:,3]==255]
def peaks(im,x,windows):
 a=im[:,max(0,x-4):x+5].astype(float).mean((1,2));a=cv2.GaussianBlur(a[:,None],(0,0),1.3)[:,0];g=np.gradient(a)
 return [int(l+np.argmax(g[l:r]*sgn)) for l,r,sgn in windows]
ws=[(30,100,-1),(640,685,-1),(675,725,1),(770,800,-1),(790,813,-1),(808,835,1)]
print('x target/native ypeaks')
for x in [190,210,220,230,250,390,430,450,470,490]:print(x,peaks(target,x,ws),peaks(raw,x,ws))
# compare base and ctx top seam color etc
Image.fromarray(target).save(O/'base-current.png')
for n,b in [('upper-left',(130,0,400,450)),('repair',(130,440,570,1020))]:
 Image.fromarray(target).crop(b).save(O/(n+'-base.png'))


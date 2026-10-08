from pathlib import Path
from PIL import Image
import numpy as np,sys
O=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
n=np.array(Image.open(O/'native.png'));b=np.array(Image.open(O.parent/'final-registration-v1/joined.png'))
for y in [220,260,280,300,320]:
 vals=[]
 for a in [b,n]:
  v=a[y-3:y+4].mean((0,2));g=np.gradient(cv2.GaussianBlur(v[None,:],(0,0),1)[0]);vals.append([int(l+np.argmax(g[l:r]*s)) for l,r,s in [(220,265,-1),(235,280,1)]])
 print('xedges',y,vals)
for x in [220,250,285,300,320]:
 vals=[]
 for a in [b,n]:
  v=a[:,x-2:x+3].mean((1,2));g=np.gradient(cv2.GaussianBlur(v[:,None],(0,0),1)[:,0]);vals.append([int(l+np.argmax(g[l:r]*s)) for l,r,s in [(35,56,-1),(57,75,-1),(76,94,1)]])
 print('yedges',x,vals)

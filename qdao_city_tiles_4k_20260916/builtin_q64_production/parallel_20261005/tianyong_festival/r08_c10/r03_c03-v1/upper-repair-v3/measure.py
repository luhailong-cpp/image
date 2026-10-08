from pathlib import Path
from PIL import Image
import numpy as np,sys
O=Path(__file__).resolve().parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
raw=np.array(Image.open(O/'native.png').convert('RGB'));base=np.array(Image.open(O.parent/'final-registration-v1/joined.png'))
ws=[(35,65,-1),(48,80,-1),(62,108,1)]
for x in [220,230,250,280,300,330,340,400,430]:
 peaks=[]
 for a in [base,raw]:
  v=a[:,x-2:x+3].astype(float).mean((1,2));g=np.gradient(cv2.GaussianBlur(v[:,None],(0,0),1)[:,0]);peaks.append([int(l+np.argmax(g[l:r]*s)) for l,r,s in ws])
 print(x,peaks)
base[0:240,230:340]=raw[0:240,230:340];Image.fromarray(base).save(O/'naive.png');Image.fromarray(base).crop((180,0,440,320)).save(O/'naive-upper.png')

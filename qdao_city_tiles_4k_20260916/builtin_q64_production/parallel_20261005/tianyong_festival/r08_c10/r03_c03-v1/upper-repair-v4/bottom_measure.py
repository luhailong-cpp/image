from pathlib import Path
from PIL import Image
import numpy as np,sys
O=Path(__file__).resolve().parent;P=O.parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor');import cv2
ims={n:np.array(Image.open(f).convert('RGB')) for n,f in [('current',O/'joined.png'),('oldctx',P/'registration-v3/context-v005.png'),('aligned',P/'registration-v3/aligned-native.png')]}
ws=[(240,300,-1),(480,545,1),(615,665,-1),(675,740,1),(870,935,-1),(910,960,1)]
for y in [1016,1032,1060]:
 for name,a in ims.items():
  v=a[y-3:y+4].mean((0,2));g=np.gradient(cv2.GaussianBlur(v[None,:],(0,0),1.2)[0]);print(y,name,[int(l+np.argmax(g[l:r]*s)) for l,r,s in ws])

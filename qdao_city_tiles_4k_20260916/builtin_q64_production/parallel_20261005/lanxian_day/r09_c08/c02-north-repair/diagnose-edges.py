from pathlib import Path
from PIL import Image
import sys,numpy as np,json
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair'
ctx=json.loads((T/'regional/context.json').read_text());n=np.array(Image.open(ctx['northCore']['file']).convert('RGB').crop((909,3981,2163,4096)));b=np.array(Image.open(R/'original/native/r01_c02.png').convert('RGB'));r=np.array(Image.open(R/'native-source01.png').convert('RGB'))
def peaks(a,y,l,h):
 z=cv2.GaussianBlur(a.astype(np.float32),(3,3),.7);v=np.linalg.norm(z[y,2:]-z[y,:-2],axis=1);out=[]
 for x in range(l+1,min(h-1,1252)):
  if v[x-1]>=max(v[max(x-3,0):x+2]) and v[x-1]>8:out.append([x,round(float(v[x-1]),2),a[y,x].tolist()])
 return out
v={}
for name,im,y in [('true',n,114),('base',b,115),('repair',r,627)]:
 v[name]={str((l,h)):peaks(im,y,l,h) for l,h in [(0,425),(425,750),(730,1010),(990,1254)]}
print(json.dumps(v));(R/'edge-profile.json').write_text(json.dumps(v,indent=2))


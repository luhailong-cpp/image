from pathlib import Path
from PIL import Image
import sys,json,numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';ctx=json.loads((T/'regional/context.json').read_text())
n=np.array(Image.open(ctx['northCore']['file']).convert('RGB').crop((909,3981,2163,4096)));w=np.array(Image.open(R/'wood-source02.png').convert('RGB'))
def grad(im):
 g=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY).astype('float32')
 return np.stack([cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3),cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)],axis=-1)
ng=grad(n);wg=grad(w);results={}
for name,(x0,y0,x1,y1) in [('cap',(700,60,870,114)),('right',(810,80,870,114)),('left',(700,60,810,114))]:
 a=ng[y0:y1,x0:x1].ravel();a=a-a.mean();scores=[]
 for dy in range(-20,25):
  for dx in range(-8,25):
   b=wg[512+y0+dy:512+y1+dy,x0+dx:x1+dx].ravel();b=b-b.mean();score=float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-7));scores.append((score,dx,dy))
 results[name]=sorted(scores,reverse=True)[:8]
(R/'wood-shift-search.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))


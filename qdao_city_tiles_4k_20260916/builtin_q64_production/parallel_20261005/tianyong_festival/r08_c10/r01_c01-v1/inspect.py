from pathlib import Path
import numpy as np,json,sys
from PIL import Image
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'config/image-generation.json').exists())
sys.path.insert(0,str(ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor'))
import cv2
npath=Path(sys.argv[1]) if len(sys.argv)>1 else P/'native.png'
n=np.array(Image.open(npath).convert('RGB'));c=np.array(Image.open(P/'context.png').convert('RGB'))
out=npath.parent/'qa-initial';out.mkdir(exist_ok=True)
for name,box in [('left',(0,115,320,1254)),('right',(880,0,1254,1254)),('leftupper',(0,115,330,450)),('leftlower',(0,1000,330,1254)),('rightcross',(940,390,1254,770))]:
 w,h=box[2]-box[0],box[3]-box[1];im=Image.new('RGB',(w*2,h));im.paste(Image.fromarray(c).crop(box),(0,0));im.paste(Image.fromarray(n).crop(box),(w,0));im.save(out/(name+'.png'))
ng=cv2.cvtColor(n,cv2.COLOR_RGB2GRAY).astype(np.float32);cg=cv2.cvtColor(c,cv2.COLOR_RGB2GRAY).astype(np.float32)
metrics=[]
for name,x,y,hh in [('leftupper',62,180,28),('lefttrim',68,366,26),('leftlower',65,1090,28),('leftbottom',65,1200,28),('rightupper',1135,110,35),('rightmid',1135,545,35),('rightflower',1140,925,35),('rightcloud',1140,1130,35)]:
 template=cg[y-hh:y+hh+1,x-hh:x+hh+1]
 search=ng[y-hh-20:y+hh+21,x-hh-20:x+hh+21]
 corr=cv2.matchTemplate(search,template,cv2.TM_CCOEFF_NORMED);_,score,_,loc=cv2.minMaxLoc(corr)
 metrics.append({'feature':name,'center':[x,y],'inverseDeltaXY':[loc[0]-20,loc[1]-20],'score':score})
(out/'match.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps(metrics))

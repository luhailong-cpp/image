from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
r=Path(r'E:\work\image\qdao_chibi_roster_v12');p=r/'review/28_low_walk_fixes/root-S-NE';c=r/'candidate-stable-body/28_moon_rabbit_artificer';records=[]
def m(im):
 a=np.array(im.convert('RGB'));fg=~((a[:,:,0]>165)&(a[:,:,1]<120)&(a[:,:,2]>150));ys,xs=np.where(fg);top=int(ys.min());dark=fg&(a[:,:,:3].mean(2)<95);w=[]
 for row in dark[top+12:top+125]:
  x=np.where(row)[0]
  if len(x):w.append(x[-1]-x[0]+1)
 return {'head_width_p90':float(np.percentile(w,90)),'height':int(ys.max()-ys.min()+1),'top':top,'bottom':int(ys.max())}
for d in ['S','NE']:
 old=Image.open(c/'source'/('walk-'+d+'-final.png')).convert('RGBA')
 for phase in [4,8]:
  i=phase-1;box=(i%4*443,i//4*443,i%4*443+443,i//4*443+443);new=Image.open(p/(d+f'{phase:02d}-cell.png'));a=m(old.crop(box));b=m(new);records.append({'d':d,'phase':phase,'original':a,'new':b,'new_head_ratio':b['head_width_p90']/a['head_width_p90']})
print(json.dumps(records));(p/'initial-low-head-metrics.json').write_text(json.dumps(records,indent=2)+'\n')


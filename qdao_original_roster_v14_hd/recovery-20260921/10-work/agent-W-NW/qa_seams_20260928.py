from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
HERE=Path(__file__).resolve().parent
rec=HERE.parents[1]
out=HERE/'ns-seams-20260928';out.mkdir(exist_ok=True)
def normalize(path):
 im=Image.open(path).convert('RGBA');fac=1024/max(im.size)*.88;im=im.resize(tuple(round(x*fac) for x in im.size),Image.Resampling.LANCZOS)
 y,x=np.where(np.array(im)[:,:,3]>8);top=int(y.min());h=int(y.max())-top
 ax=float(np.median(x[y<top+max(1,int(h*.42))]));dy=942-int(y.max());dx=round(512-ax)
 result=Image.new('RGBA',(1024,1024));result.paste(im,(dx,dy));return result,{'factor':fac,'delta':[dx,dy]}
rows=[]
for d,seq in [('N',['N15-v1','N16-v1','N16-v5','N01-v1','N02-v1']),('S',['S15-v1','S16-v1','S16-v2','S01-v2','S02-v1'])]:
 for theme,color in [('dark','#18212c'),('light','#f0ede5')]:
  sheet=Image.new('RGB',(5*512,542),color);draw=ImageDraw.Draw(sheet)
  for k,a in enumerate(seq):
   raw=rec/'10-generation'/a/'raw.png';im,normal=normalize(raw);im.save(out/f'{a}-aligned.png')
   if theme=='dark':rows.append({'attempt':a,'rawSHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'normalization':normal})
   im=im.resize((512,512),Image.Resampling.LANCZOS);sheet.paste(im,(k*512,0),im);draw.text((k*512+12,518),a,fill='white' if theme=='dark' else 'black')
  sheet.save(out/f'{d}-{theme}-compare.jpg',quality=97)
(out/'source-bindings.json').write_text(json.dumps(rows,indent=2)+'\n')
print(out)

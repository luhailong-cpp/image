from pathlib import Path
from PIL import Image
import numpy as np,json
R=Path(__file__).resolve().parents[2]
def measure(p):
 a=np.array(Image.open(p).convert('RGBA'));rr,g,b=a[:,:,0].astype(float),a[:,:,1].astype(float),a[:,:,2].astype(float)
 m=(rr>190)&(rr>g*1.035)&(g>b*1.035)&(a[:,:,3]>200);m[:300]=False;m[610:]=False;m[:,:300]=False;m[:,1050:]=False
 pts=set(zip(*np.where(m)));best=[]
 while pts:
  todo=[pts.pop()];comp=[]
  while todo:
   y,x=todo.pop();comp.append((y,x))
   for pt in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
    if pt in pts:pts.remove(pt);todo.append(pt)
  if len(comp)>len(best):best=comp
 ys,xs=zip(*best)
 return {'bounds':list(map(int,[min(xs),min(ys),max(xs)+1,max(ys)+1])),'width':int(max(xs)-min(xs)+1),'height':int(max(ys)-min(ys)+1),'area':len(best)}
rows=[]
for d in ('SW','SE'):
 for n in (4,5,7):
  src=sorted((R/'run/staging').glob(f'south-bamboo-contact-{d}-{n:02}-v[0-9].png'))[-1]
  req=json.loads((R/f'provenance/{src.stem}.request.json').read_text(encoding='utf-8'))
  base=Path(req['submittedParameters']['referenced_image_paths'][0])
  a,b=measure(base),measure(src)
  rows.append({'d':d,'n':n,'base':str(base),'candidate':src.name,'baseFace':a,'candidateFace':b,'widthRatio':b['width']/a['width']})
(R/'audit/south-contact-face-measures.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))


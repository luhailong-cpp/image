from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[1]
S=json.loads((R/'10-work/selection-current.json').read_text(encoding='utf-8-sig'))
S.update(json.loads((H/'selection-W-review.json').read_text()))
S.update(json.loads((H/'selection-NW-review.json').read_text()))
S.update(json.loads((H/'selection-updates-20260928.json').read_text()))
S['NW01']={'archive':'NW01-v4'}
O=H/'static-review-final-20260928';O.mkdir(exist_ok=True)
rows=[]
for d in ['N','S','W','NW']:
 imgs={}
 for i in range(1,17):
  k=f'{d}{i:02}';a=S[k]['archive'];raw=R/'10-generation'/a/'raw.png';im=Image.open(raw).convert('RGBA')
  fac=1024/max(im.size)*.84;normal=im.resize(tuple(round(v*fac) for v in im.size),Image.Resampling.LANCZOS)
  ar=np.asarray(normal)[:,:,3];y,x=np.where(ar>8)
  ax=S[k].get('nativeRootX',620)*fac;ay=S[k].get('nativeRootY',1195)*fac
  delta=(round(512-ax),round(942-ay));im=Image.new('RGBA',(1024,1024));im.paste(normal,delta);imgs[i]=im
  rows.append({'slot':k,'attempt':a,'rawSHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'factor':fac,'translation':delta,'rootMethod':'fixed nativeRoot=(%s,1195)'%{'N':635,'S':605,'NW':620}.get(d,'') if d!='W' else 'legacy upper42percent median and maxAlpha temporarily'})
 for theme,col in [('light','#f0ede5'),('dark','#18212c')]:
  for inds in [list(range(1,9)),list(range(9,17)),[15,16,1,2]]:
   sz=384 if len(inds)>4 else 512
   sh=Image.new('RGB',(4*sz,(sz+24)*(2 if len(inds)>4 else 1)),col);dr=ImageDraw.Draw(sh)
   for j,i in enumerate(inds):
    im=imgs[i].resize((sz,sz),Image.Resampling.LANCZOS);xx=j%4*sz;yy=j//4*(sz+24);sh.paste(im,(xx,yy),im);dr.text((xx+8,yy+sz+3),f'{d}{i:02} '+S[f'{d}{i:02}']['archive'],fill='black' if theme=='light' else 'white')
   sh.save(O/f'{d}-{theme}-{inds[0]:02}-{inds[-1]:02}.jpg',quality=96)
  sh=Image.new('RGB',(4*512,2*344),col);dr=ImageDraw.Draw(sh)
  for j,i in enumerate([1,3,5,7,9,11,13,15]):
   im=imgs[i].crop((250,650,762,964));xx=j%4*512;yy=j//4*344;sh.paste(im,(xx,yy),im);dr.text((xx+8,yy+318),f'{d}{i:02}',fill='black' if theme=='light' else 'white')
  sh.save(O/f'{d}-{theme}-feet.jpg',quality=96)
(O/'source-bindings.json').write_text(json.dumps({'madeAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'static candidate QA only','frames':rows},indent=2))
print(O)

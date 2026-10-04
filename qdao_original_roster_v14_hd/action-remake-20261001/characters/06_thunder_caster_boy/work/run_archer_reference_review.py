import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];A=R.parent/'09_bamboo_archer_girl'
m=json.loads((A/'manifest.json').read_text(encoding='utf-8-sig'));rows=[]
for d in ['E','W']:
 seq=next(x for x in m['sequences'] if x['action']=='run' and x['direction']==d)
 im=Image.new('RGB',(1024,1136),(33,49,55));dr=ImageDraw.Draw(im)
 for j,f in enumerate(seq['frames']):
  p=A/f['file'];sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==f['sha256']
  a=Image.open(p).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS);x=j%4*256;y=j//4*284
  im.paste(a,(x,y),a);dr.text((x+8,y+260),f'09 / {d} / {f["frame"]:02d}',fill=(248,240,210));rows.append({'file':str(p),'sha256':sha,'direction':d,'frame':f['frame']})
 im.save(R/'review'/f'run_archer_{d}_reference_contact_20261003.png')
(R/'review/run_archer_EW_reference_sources_20261003.json').write_text(json.dumps({'manifest':str(A/'manifest.json'),'manifestSHA':hashlib.sha256((A/'manifest.json').read_bytes()).hexdigest(),'operation':'Read-only originals, same full-canvas preview scale, no image mutation. Local anatomy comparison only.','sources':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

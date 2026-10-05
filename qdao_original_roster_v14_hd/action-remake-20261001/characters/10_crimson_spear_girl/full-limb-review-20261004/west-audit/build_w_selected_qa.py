from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
r=Path(__file__).resolve().parents[2];out=r/'full-limb-review-20261004/west-audit';versions={9:'09-v2',10:'10-v1',11:'11-v6',12:'12-v1'}
paths={i:r/f'full-limb-review-20261004/run-W/{versions[i]}/native.png' if i in versions else r/f'runtime/run/W/{i:02}.png' for i in range(1,17)}
for kind,indices in [('full',range(1,17)),('lower',range(5,15))]:
 w,h=(256,276) if kind=='full' else (425,350);cols=4 if kind=='full' else 5;rows=(len(indices)+cols-1)//cols;o=Image.new('RGB',(cols*w,rows*h),(239,236,226));d=ImageDraw.Draw(o);sources=[]
 for idx,i in enumerate(indices):
  p=paths[i];im=Image.open(p).convert('RGBA');im=im.resize((1024,1024),Image.Resampling.LANCZOS)
  if kind=='lower':im=im.crop((360,650,785,980))
  else:im=im.resize((256,256),Image.Resampling.LANCZOS)
  x=(idx%cols)*w;y=(idx//cols)*h;o.paste(im,(x,y+20),im);d.text((x+5,y+4),f'W{i:02} '+versions.get(i,'runtime'),fill=(20,20,20));sources.append({'slot':f'run/W/{i:02}','file':p.relative_to(r).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 fp=out/f'W-selected-{kind}.jpg';o.save(fp,quality=98);fp.with_suffix('.jpg.generation.json').write_text(json.dumps({'kind':'visual-QA-derivative','method':'full-canvas native to1024 normalization only; fixed crops/tiles; no asset edits','sources':sources},indent=2),encoding='utf-8')

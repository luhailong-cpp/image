from pathlib import Path
import json,sys,hashlib
from PIL import Image,ImageDraw
import numpy as np
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from export_frame import run as export
from apply_registration import apply
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];sel={}
for d in ('SW','SE'):
 for n in (1,2,4,5,6,7,8,12,13,14,15,16):
  found=sorted((R/'run/staging').glob(f'south-bamboo-contact-{d}-{n:02}-v[0-9].png'))
  if not found:continue
  src=found[-1];label=src.stem;req=json.loads((R/f'provenance/{label}.request.json').read_text(encoding='utf-8'))
  reg=json.loads((R/f'run/{d}/registration.json').read_text(encoding='utf-8-sig'));base=3 if n<=8 else 11
  row=next(x for x in reg['frames'] if x['file']==f'run/{d}/{base:02}.png')
  dest=src.with_name(src.stem+'-registered.png');export(src,dest)
  rows.append({'file':dest.relative_to(R).as_posix(),'sha256':sha(dest),'srcRoot':row['srcRoot'],'formalTarget':f'run/{d}/{n:02}.png','selectedNative':src.relative_to(R).as_posix()})
  sel[(d,n)]=dest
rp=R/'run/staging/south-bamboo-oblique-candidate-registration.json'
rp.write_text(json.dumps({'globalScale':.8,'targetRoot':[512,942],'frames':rows},indent=2),encoding='utf-8')
apply(rp)
for d in ('SW','SE'):
 out=Image.new('RGB',(1280,1408),(230,235,235));dr=ImageDraw.Draw(out)
 for n in range(1,17):
  p=sel.get((d,n),R/f'run/{d}/{n:02}.png');im=Image.open(p).resize((320,320),Image.Resampling.LANCZOS)
  x=(n-1)%4*320;y=(n-1)//4*352;out.paste(im,(x,y),im)
  dr.text((x+8,y+322),f'{d}/{n:02} '+('candidate' if (d,n)in sel else 'current'),fill=(10,20,30))
 out.save(R/f'run/staging/south-bamboo-contact-{d}-latest-review.jpg',quality=94)
print(json.dumps({'candidates':len(rows)}))


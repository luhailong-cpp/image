from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
for d in ('E','W'):
 out=Image.new('RGB',(1200,1320),'#eee9db');dr=ImageDraw.Draw(out);sources=[]
 for f in range(1,17):
  cand=list((R/'provenance/run').glob(f'stancepairs_{d}_{f:02}_attempt*.png'))
  p=sorted(cand)[-1] if cand else R/f'frames/run/{d}/frame_{f:02}.png'
  im=Image.open(p).convert('RGBA');im.thumbnail((300,300))
  x=((f-1)%4)*300;y=((f-1)//4)*330
  out.paste(im,(x,y+25),im);dr.text((x+8,y+5),f'{d} {f:02} '+('NEW' if cand else 'KEEP'),fill='black')
  sources.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 path=R/f'provenance/run/stancepairs_{d}_candidate_contact.png';out.save(path)
 path.with_suffix('.png.generation.json').write_text(json.dumps({'operation':'review_contact_composite_only','derivedFrom':sources},indent=2),encoding='utf8')
 print(path)


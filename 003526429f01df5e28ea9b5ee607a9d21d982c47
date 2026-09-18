from pathlib import Path
import json,shutil,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
r=Path('E:/work/image/qdao_original_roster_v13'); c=r/'candidate/00_reference_topright_boy'; hist=r/'history/00-before-visual-repair'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');shutil.copytree(c,hist)
print('snapshot',hist)
review=r/'review/00_reference_topright_boy';review.mkdir(exist_ok=True)
for d in ['N','NE','E','SE','S','SW','W','NW']:
 im=Image.open(c/f'review/{d}-contact.png');im.resize((1100,round(im.height*1100/im.width))).save(review/f'{d}-full-contact.jpg',quality=82,optimize=True)
rec=json.loads((c/'processing/frame-sources.json').read_text())
evidence=[]
for label,frames in [('A',[2,6,10,14]),('B',[4,8,12,16])]:
 b=Image.new('RGB',(900,900),(255,0,255))
 for i,f in enumerate(frames):
  p=rec[f'walk/S/{f:02d}.png']['source'];raw=Image.open(c/p['path']).convert('RGBA');cell=raw.crop(p['cell_xyxy']);flat=Image.new('RGB',cell.size,(255,0,255));flat.paste(cell,(0,0),cell);y,x=divmod(i,2);b.paste(flat.resize((450,450),Image.Resampling.LANCZOS),(x*450,y*450));evidence.append({'board':label,'slot':i,'frame':f,'source':p})
 b.save(review/f'S-repair-{label}.jpg',quality=79,optimize=True)
(review/'S-repair-reference-provenance.json').write_text(json.dumps({'purpose':'original full source cell reference layout; no new art','entries':evidence},indent=2))
print('references_ready')
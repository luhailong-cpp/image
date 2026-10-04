from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
r=Path(__file__).resolve().parents[2]
rows=json.loads((r/'provenance/attack/selection-W.json').read_text(encoding='utf-8-sig'))
out=[];sheet=Image.new('RGB',(1280,1050),'#bdc7d1');draw=ImageDraw.Draw(sheet)
for i,x in enumerate(rows):
 p=r/x['file'];im=Image.open(p).convert('RGBA');a=im.getchannel('A')
 edge=max(max(a.crop((0,0,1,im.height)).get_flattened_data()),max(a.crop((im.width-1,0,im.width,im.height)).get_flattened_data()),max(a.crop((0,0,im.width,1)).get_flattened_data()),max(a.crop((0,im.height-1,im.width,im.height)).get_flattened_data()))
 bb=a.point(lambda z:255 if z>128 else 0).getbbox()
 out.append(dict(frame=x['frame'],file=x['file'],size=im.size,bboxAlpha128=bb,canvasEdgeMaxAlpha=edge,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 im.thumbnail((320,320));xx=i%4*320;yy=i//4*350;sheet.paste(im,(xx,yy),im)
 draw.text((xx+8,yy+325),f'W{x["frame"]:02d} '+p.name,fill='black')
 print(x['frame'],bb,edge)
sheet.save(r/'provenance/attack/W-review-contact-current.jpg',quality=95)
(r/'provenance/attack/W-pixel-audit-current.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')


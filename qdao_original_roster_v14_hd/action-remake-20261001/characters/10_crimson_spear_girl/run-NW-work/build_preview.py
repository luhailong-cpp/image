from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
d=Path(__file__).parent
sel=json.loads((d/'selection.json').read_text())
frames=[]
canvas=[]
for i in range(1,17):
 f=sel['slots'][f'run/NW/{i:02d}'];p=d.parent/f
 im=Image.open(p).convert('RGBA');c=Image.new('RGBA',(1024,1024))
 c.alpha_composite(im.resize((860,860),Image.Resampling.LANCZOS),(66,135));canvas.append(c)
 frames.append({'slot':i,'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'mode':im.mode})
sheet=Image.new('RGB',(1280,1392),'#e9e8e1');dr=ImageDraw.Draw(sheet)
detail=Image.new('RGB',(1440,1160),'#e9e8e1');dd=ImageDraw.Draw(detail)
for i,(p,c) in enumerate(zip(frames,canvas)):
 x=i%4*320;y=i//4*348;thumb=c.resize((320,320))
 sheet.paste(thumb,(x,y),thumb)
 # Root only: NW feet follow perspective contact tracks, not horizontal-foot snap.
 rx=x+512*320/1024;ry=y+942*320/1024
 dr.line((rx-10,ry,rx+10,ry),fill='#c25a40');dr.line((rx,ry-6,rx,ry+6),fill='#c25a40')
 dr.text((x+6,y+323),str(i+1).zfill(2)+' '+p['file'],fill='#222')
 im=Image.open(d/p['file']).convert('RGBA');cr=im.crop((350,750,930,1245)).resize((338,288))
 x=i%4*360;y=i//4*290;detail.paste(cr,(x,y),cr);dd.text((x+5,y+5),str(i+1).zfill(2),fill='#222')
sheet.save(d/'contact-grounding.jpg',quality=95);detail.save(d/'feet-audit.jpg',quality=95)
(d/'contact-grounding.jpg.generation.json').write_text(json.dumps({'operation':'Diagnostic preview fixed full-canvas scale860/1254 offset66,135, root512,942. No per-frame shifts/bbox resize','sources':frames},indent=2),encoding='utf8')
(d/'frames-audit.json').write_text(json.dumps({'selected':16,'unique':len(set(f['sha256'] for f in frames)),'frames':frames},indent=2),encoding='utf8')
print('selected',len(frames),'unique',len(set(f['sha256'] for f in frames)))


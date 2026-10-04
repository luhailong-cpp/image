from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
d=Path(__file__).parent;base=d.parent
s=json.loads((base/'attack-work/selection.json').read_text(encoding='utf8'))
refs=[];sheet=Image.new('RGB',(1280,1056),'#e9e8e1');dr=ImageDraw.Draw(sheet)
for j in range(12):
 slot=f'attack/W/{j+1:02d}';p=base/s['slots'][slot];im=Image.open(p).convert('RGBA');thumb=im.resize((320,320))
 x=j%4*320;y=j//4*352;sheet.paste(thumb,(x,y),thumb);dr.line((x,y+1135*320/1254,x+320,y+1135*320/1254),fill='#b85c45');dr.text((x+5,y+322),slot+' '+p.name,fill='#222')
 refs.append({'slot':slot,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
sheet.save(d/'before-attack-W.jpg',quality=95)
(d/'input-selection-snapshot.json').write_text(json.dumps({'sources':refs},indent=2),encoding='utf8')
a=base.parent/'09_bamboo_archer_girl';m=json.loads((a/'manifest.json').read_text(encoding='utf8'))
chosen=next(s for s in m['sequences'] if s['label']=='attack/W')['frames']
sheet=Image.new('RGB',(1120,924),'#eeeae1');dr=ImageDraw.Draw(sheet);audit=[]
for j,f in enumerate(chosen):
 p=a/f['file'];im=Image.open(p).convert('RGBA');thumb=im.resize((280,280));x=j%4*280;y=j//4*308;sheet.paste(thumb,(x,y),thumb);dr.text((x+5,y+282),f['slot'],fill='#222')
 actual=hashlib.sha256(p.read_bytes()).hexdigest();audit.append({'slot':f['slot'],'path':str(p),'actualSHA':actual,'manifestSHA':f['sha256'],'matches':actual==f['sha256']})
sheet.save(d/'09-attack-W-reference.jpg',quality=95)
(d/'09-reference-read-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf8')
print('09 reference12, hashes match',all(f['matches'] for f in audit))


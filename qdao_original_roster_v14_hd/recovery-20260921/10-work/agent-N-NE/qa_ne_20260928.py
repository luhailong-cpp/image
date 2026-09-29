import json, hashlib
from pathlib import Path
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[2]
A=Path(__file__).resolve().parent
sel=json.loads((A/'selection.json').read_text(encoding='utf-8-sig'))
sel['NE06']={'archive':'NE06-v2','review':'static_candidate: image edit corrects enlarged right swing boot; left planted support and right advancing phase retained. Actual model unexposed; final combined loop pending.'}
sel['NE08']={'archive':'NE08-v3','review':'static_candidate: near right forward low precontact; far left trailing toe supports. Right long-tail foreground curl relaxes behind forearm to bridge into09. Static both-background checks; final combined loop pending.'}
sel['NE15']={'archive':'NE15-v4','review':'static_candidate: left low airborne forward, right flat support; loose right tail begins forward S followthrough before16. Native hand is partially occluded by hair; no extra limb visible. Final combined loop pending.'}
sel['NE16']={'archive':'NE16-v4','review':'static_candidate: far left low precontact and near right toe support with raised heel; tail advances across forearm before01. Static both-background checks; final combined loop pending.'}
for s,v in sel.items():
 if s.startswith('NE'):
  v['nativeRootX']=730
  v['nativeRootY']=1195
  v['anchorReason']='Fixed virtual pelvis-ground projection across NE, measured native-grid inspection. Preserve farther contact feet at higher screen Y and true swing clearance; never use lowest visible alpha as support foot.'
(A/'selection.json').write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
out=A/'qa-ne-20260928';out.mkdir(exist_ok=True)
slots=[f'NE{i:02d}' for i in range(1,17)]+['NEidle']
raws={s:Image.open(R/'10-generation'/sel[s]['archive']/'raw.png').convert('RGBA') for s in slots}
for bg,c in [('light',(244,239,227)),('dark',(30,39,43))]:
 for g,keys in [('01-08',slots[:8]),('09-16',slots[8:16]),('seam',['NE15','NE16','NE01','NE02']),('halfseam',['NE07','NE08','NE09','NE10']),('idle',['NEidle'])]:
  sheet=Image.new('RGB',(512*min(4,len(keys)),546*((len(keys)+3)//4)),c)
  for n,s in enumerate(keys):
   im=raws[s].resize((512,512),Image.Resampling.LANCZOS);x=(n%4)*512;y=(n//4)*546
   sheet.paste(im,(x,y),im);ImageDraw.Draw(sheet).text((x+10,y+518),s+' '+sel[s]['archive'],fill=(255,255,255) if bg=='dark' else(0,0,0))
  sheet.save(out/f'{bg}-{g}.jpg',quality=96)
 for g in range(4):
  keys=slots[g*4:g*4+4];sheet=Image.new('RGB',(2048,640),c)
  for n,s in enumerate(keys):
   im=raws[s].crop((490,830,1002,1230)).resize((512,600),Image.Resampling.LANCZOS)
   sheet.paste(im,(n*512,0),im);ImageDraw.Draw(sheet).text((n*512+10,610),s,fill=(255,255,255) if bg=='dark' else(0,0,0))
  sheet.save(out/f'{bg}-feet-{g+1}.jpg',quality=96)
rows=[]
for s,im in raws.items():
 p=R/'10-generation'/sel[s]['archive']/'raw.png'
 rows.append({'slot':s,'archive':sel[s]['archive'],'size':im.size,'alpha':im.getchannel('A').getextrema(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pixelSHA':hashlib.sha256(im.tobytes()).hexdigest()})
assert len({r['pixelSHA'] for r in rows})==17
(out/'source-check.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(out)

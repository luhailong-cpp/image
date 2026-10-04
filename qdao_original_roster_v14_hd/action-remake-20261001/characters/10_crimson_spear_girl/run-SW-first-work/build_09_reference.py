from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ours=Path(__file__).parent
ar=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl')
m=json.loads((ar/'manifest.json').read_text(encoding='utf-8-sig'))
audit=[]
for direction in ['W','NW','SW']:
 s=next(s for s in m['sequences'] if s['label']=='run/'+direction)
 sheet=Image.new('RGB',(1120,1232),'#eeeae1');dr=ImageDraw.Draw(sheet)
 for i,f in enumerate(s['frames']):
  p=ar/f['file'];im=Image.open(p).convert('RGBA');thumb=im.resize((280,280))
  x=i%4*280;y=i//4*308;sheet.paste(thumb,(x,y),thumb);dr.text((x+8,y+283),direction+' '+str(f['frame']).zfill(2),fill='#222')
  actual=hashlib.sha256(p.read_bytes()).hexdigest()
  audit.append({'slot':f['slot'],'file':str(p),'manifestSHA':f['sha256'],'actualSHA':actual,'matches':actual==f['sha256']})
 sheet.save(ours/('09-reference-'+direction+'.jpg'),quality=94)
(ours/'09-reference-read-audit.json').write_text(json.dumps({'readOnlyOtherCharacter':True,'references':audit},indent=2),encoding='utf8')
print('Reference runtime read48, hashes valid',all(a['matches'] for a in audit))


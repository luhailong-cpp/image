from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from export_frame import run as export
from apply_registration import apply
selected={'S/05':'south-bamboo-S-05-v1','S/13':'south-bamboo-S-13-v1','SW/05':'south-bamboo-SW-05-v2','SW/12':'south-bamboo-SW-12-v2','SW/13':'south-bamboo-SW-13-v3','SE/12':'south-bamboo-SE-12-v3','SE/13':'south-bamboo-SE-13-v1'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for key,label in selected.items():
 d,n=key.split('/')
 src=R/'run/staging'/f'{label}.png'
 out=R/'run/staging'/f'{label}-registered.png'
 export(src,out)
 old=json.loads((R/'run'/d/'registration.json').read_text(encoding='utf-8-sig'))
 row=next(v for v in old['frames'] if v['file']==f'run/{key}.png')
 rows.append({'file':out.relative_to(R).as_posix(),'sha256':sha(out),'srcRoot':row['srcRoot'],'basis':'Original anatomical pelvic root retained after upper-body-locked edit; common source ground y960; no per-frame foot fitting','formalTarget':f'run/{key}.png','selectedNative':src.relative_to(R).as_posix()})
reg={'schemaVersion':1,'globalScale':.8,'targetRoot':[512,942],'method':'whole native canvas exported to1024 then single common global .8 transform; candidate only','frames':rows}
p=R/'run/staging/south-bamboo-candidate-registration.json'
p.write_text(json.dumps(reg,ensure_ascii=False,indent=2),encoding='utf-8')
apply(p)
sheet=Image.new('RGB',(1200,len(rows)*300),(231,234,233));dr=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
 k=row['formalTarget']
 d,n=Path(k).parts[1:]
 ref=R.parent/'09_bamboo_archer_girl/runtime/run'/d/n
 paths=[R/k,R/row['file'],ref]
 for col,ip in enumerate(paths):
  im=Image.open(ip).convert('RGBA');im.thumbnail((285,285));sheet.paste(im,(col*400+60,i*300),im)
  dr.text((col*400+10,i*300+282),['14 current '+k,'14 candidate '+k,'09 guide '+k][col],fill=(20,30,40))
sheet.save(R/'run/staging/south-bamboo-candidate-comparison.jpg',quality=94)
print(json.dumps({'candidates':len(rows),'comparison':'run/staging/south-bamboo-candidate-comparison.jpg'}))


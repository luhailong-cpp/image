from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from export_frame import run as export
from apply_registration import apply
keys=['S/05','S/13','SW/05','SW/12','SW/13','SE/13']
rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for k in keys:
 d,n=k.split('/');label='south-bamboo-scale-'+d+'-'+n+'-v1'
 src=R/'run/staging'/f'{label}.png';out=R/'run/staging'/f'{label}-registered.png'
 export(src,out)
 old=json.loads((R/'run'/d/'registration.json').read_text(encoding='utf-8-sig'))
 row=next(v for v in old['frames'] if v['file']==f'run/{k}.png')
 rows.append({'file':out.relative_to(R).as_posix(),'sha256':sha(out),'srcRoot':row['srcRoot'],'formalTarget':f'run/{k}.png','selectedNative':src.relative_to(R).as_posix()})
rp=R/'run/staging/south-bamboo-scale-candidate-registration.json'
rp.write_text(json.dumps({'globalScale':.8,'targetRoot':[512,942],'frames':rows},indent=2),encoding='utf-8')
apply(rp)
for k,row in zip(keys,rows):
 d,nn=k.split('/');n=int(nn)
 paths=[R/f'run/{d}/{n-1:02}.png',R/row['file'],R/f'run/{d}/{n+1:02}.png',R/f'run/{d}/{n:02}.png']
 labels=[f'{d}/{n-1:02}',f'{k} scale candidate',f'{d}/{n+1:02}',f'{k} current']
 sheet=Image.new('RGB',(1600,720),(226,233,232));draw=ImageDraw.Draw(sheet)
 for i,(p,label) in enumerate(zip(paths,labels)):
  im=Image.open(p).convert('RGBA');small=im.resize((400,400),Image.Resampling.LANCZOS)
  sheet.paste(small,(400*i,0),small)
  crop=im.crop((250,230,800,630));crop.thumbnail((400,290))
  sheet.paste(crop,(400*i,420),crop);draw.text((400*i+12,400),label,fill=(20,30,40))
 sheet.save(R/f'run/staging/south-bamboo-scale-{d}-{nn}-review.jpg',quality=94)
print(json.dumps({'prepared':keys}))

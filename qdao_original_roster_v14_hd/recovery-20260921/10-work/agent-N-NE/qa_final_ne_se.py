from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[2];C=R/'10-delivery-preview/current';O=Path(__file__).resolve().parent/'final-NE-SE-QA';O.mkdir(exist_ok=True)
M=json.loads((C/'manifest.json').read_text(encoding='utf-8'));rows=[]
for D in ['NE','SE']:
 K=[f'{i:02}' for i in range(1,17)];I={k:Image.open(C/'walk'/D/(k+'.png')).convert('RGBA') for k in K}
 for k,im in I.items():
  p=C/'walk'/D/(k+'.png');h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==M['frames'][D+k]['sha256'];rows.append({'slot':D+k,'path':str(p),'sha256':h,'archive':M['frames'][D+k]['archive'],'size':im.size,'alphaRange':im.getchannel('A').getextrema()})
 for name,col in [('light','#f4efe3'),('dark','#1e272b')]:
  for group,keys in [('01-08',K[:8]),('09-16',K[8:]),('seam',['15','16','01','02']),('06-09',['06','07','08','09'])]:
   im=Image.new('RGB',(2048,546*((len(keys)+3)//4)),col)
   for n,k in enumerate(keys):
    f=I[k].resize((512,512),Image.Resampling.LANCZOS);x=n%4*512;y=n//4*546;im.paste(f,(x,y),f);ImageDraw.Draw(im).text((x+10,y+519),D+k,fill='white' if name=='dark' else 'black')
   im.save(O/f'{D}-{name}-{group}.jpg',quality=97)
  for g in range(4):
   im=Image.new('RGB',(2048,575),col)
   for n,k in enumerate(K[g*4:g*4+4]):
    f=I[k].crop((280,650,790,1000)).resize((512,540),Image.Resampling.LANCZOS);im.paste(f,(n*512,0),f);ImageDraw.Draw(im).text((n*512+10,548),D+k,fill='white' if name=='dark' else 'black')
   im.save(O/f'{D}-{name}-feet-{g+1}.jpg',quality=97)
  for k in ['06','07','08','09','15','16','01','02']:
   im=Image.new('RGBA',(1024,1024),col);im.alpha_composite(I[k]);im.convert('RGB').save(O/f'{D}{k}-{name}-1024.jpg',quality=97)
(O/'examined-outputs.json').write_text(json.dumps({'manifestCreatedAt':M['createdAt'],'manifestSHA':hashlib.sha256((C/'manifest.json').read_bytes()).hexdigest(),'frames':rows},indent=2)+'\n',encoding='utf-8')
print(O)

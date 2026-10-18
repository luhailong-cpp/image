from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import hashlib,json
T=Path(__file__).resolve().parents[1];O=T/'pipeline/output/f76f3c3097821e90';Q=T/'pipeline/qa/resume-20261016-v01'
assert not Q.exists();Q.mkdir(parents=True)
source=O/'r13_c04.candidate.png';im=Image.open(source).convert('RGB');assert im.size==(4096,4096)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={'tile':'r13_c04','createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':{'file':str(source),'sha256':sha(source),'pixels':[4096,4096]},'assembly':{'file':str(O/'assembly.json'),'sha256':sha(O/'assembly.json')},'nativeCrops':[],'panels':[],'resampling':False,'gameArt':False,'internalAccepted':False,'formalAccepted':False}
def crop(name,box):
 p=Q/(name+'.png');c=im.crop(box);c.save(p);d['nativeCrops'].append({'id':name,'file':str(p),'sha256':sha(p),'cropBox':list(box),'pixels':list(c.size),'sourceSha256':d['source']['sha256']});return c
for axis in 'VH':
 for join in range(1,4):
  panel=Image.new('RGB',(920,1044) if axis=='V' else (1024,1000),(35,35,35));draw=ImageDraw.Draw(panel);ids=[]
  for seg in range(4):
   name=f'{axis}{join}-{seg+1}';ids.append(name)
   box=(join*1024-115,seg*1024,join*1024+115,(seg+1)*1024) if axis=='V' else (seg*1024,join*1024-115,(seg+1)*1024,join*1024+115)
   c=crop(name,box);xy=(seg*230,20) if axis=='V' else (0,seg*250+20);panel.paste(c,xy);draw.text((seg*230+4,3) if axis=='V' else (4,seg*250+3),name,fill='white')
  p=Q/f'{axis}{join}-panel.png';panel.save(p);d['panels'].append({'id':f'{axis}{join}-panel','file':str(p),'sha256':sha(p),'cropIds':ids,'pixels':list(panel.size),'resampling':False})
for row in range(1,4):
 panel=Image.new('RGB',(1536,532),(35,35,35));draw=ImageDraw.Draw(panel);ids=[]
 for col in range(1,4):
  name=f'X{row}-{col}';ids.append(name);c=crop(name,(col*1024-256,row*1024-256,col*1024+256,row*1024+256));panel.paste(c,((col-1)*512,20));draw.text(((col-1)*512+4,3),name,fill='white')
 p=Q/f'X{row}-panel.png';panel.save(p);d['panels'].append({'id':f'X{row}-panel','file':str(p),'sha256':sha(p),'cropIds':ids,'pixels':list(panel.size),'resampling':False})
(Q/'manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qa':str(Q),'cropCount':len(d['nativeCrops']),'panelCount':len(d['panels']),'sourceSha256':d['source']['sha256']}))

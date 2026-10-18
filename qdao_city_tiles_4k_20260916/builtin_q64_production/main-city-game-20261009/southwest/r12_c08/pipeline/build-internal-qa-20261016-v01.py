from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
from datetime import datetime,timezone
b=Path(__file__).resolve().parent
assembly=b/'output/583d5fd2cff421dd/assembly.json'
a=json.loads(assembly.read_text(encoding='utf-8-sig'))
src=Path(a['output']['file']); im=Image.open(src).convert('RGB')
out=b/'qa/full16-internal-20261016-v01';out.mkdir(exist_ok=False)
items=[];panels=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert im.size==(4096,4096) and sha(src)==a['output']['sha256']
for r in range(4):
 panel=Image.new('RGB',(750,1060),(40,43,48));d=ImageDraw.Draw(panel);ids=[]
 for j,x in enumerate([1024,2048,3072]):
  box=[x-115,r*1024,x+115,(r+1)*1024];crop=im.crop(box);key=f'V{j+1}-row{r+1}';cp=out/(key+'.png');crop.save(cp);panel.paste(crop,(j*250,36));d.text((j*250,8),key,fill='white')
  items.append({'id':key,'file':str(cp),'sha256':sha(cp),'box':box,'size':list(crop.size),'resampling':False});ids.append(key)
 pp=out/f'V-row{r+1}.panel.png';panel.save(pp);panels.append({'file':str(pp),'sha256':sha(pp),'items':ids,'resampling':False})
for j,y in enumerate([1024,2048,3072]):
 panel=Image.new('RGB',(1024,1040),(40,43,48));d=ImageDraw.Draw(panel);ids=[]
 for c in range(4):
  box=[c*1024,y-115,(c+1)*1024,y+115];crop=im.crop(box);key=f'H{j+1}-col{c+1}';cp=out/(key+'.png');crop.save(cp);panel.paste(crop,(0,c*260+28));d.text((4,c*260+8),key,fill='white')
  items.append({'id':key,'file':str(cp),'sha256':sha(cp),'box':box,'size':list(crop.size),'resampling':False});ids.append(key)
 pp=out/f'H-boundary{j+1}.panel.png';panel.save(pp);panels.append({'file':str(pp),'sha256':sha(pp),'items':ids,'resampling':False})
data={'tile':a['tile'],'createdAtUtc':datetime.now(timezone.utc).isoformat(),'assembly':str(assembly),'assemblySha256':sha(assembly),'source':str(src),'sourceSha256':sha(src),'nativeSources':a['nativeSources'],'cropCount':24,'items':items,'panels':panels,'internalAccepted':False,'formalAccepted':False,'generatedPanelsAreNotVisualAcceptance':True}
(out/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(out/'manifest.json'),'panels':[x['file'] for x in panels]}))


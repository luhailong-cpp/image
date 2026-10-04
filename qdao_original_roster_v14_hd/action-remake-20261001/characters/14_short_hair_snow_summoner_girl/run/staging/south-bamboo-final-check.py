from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];hashes=[]
for d in ('SW','SE'):
 audit=json.loads((R/f'audit/contact-{d}-review.json').read_text(encoding='utf-8'))
 assert len(audit['frames'])==16 and len(audit['contacts'])==2 and len(audit['positionPairs'])==8
 assert audit['contacts'][0]['frames']==list(range(1,9)) and audit['contacts'][1]['frames']==list(range(9,17))
 sheet=Image.new('RGB',(1280,1408),(230,235,235));dr=ImageDraw.Draw(sheet)
 for n,frame in enumerate(audit['frames'],1):
  p=R/frame['file'];meta=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p)
  h=sha(p);assert h==frame['sha256']==meta['sha256'];assert im.size==(1024,1024) and im.mode=='RGBA';hashes.append(h)
  assert meta['registrationTransform']['globalScale']==.8 and meta['registrationTransform']['targetRoot']==[512,942]
  src=R/meta['derivedFrom']['file']
  if src.exists():
   assert sha(src)==meta['derivedFrom']['sha256'];native=Image.open(src);assert min(native.size)>=1024
   nr=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8-sig'))
   assert nr['actualModel'] is None and nr['actualQuality'] is None
  else:assert meta['derivedFrom'].get('bitmapRemovedAfterFinalVerification') is True
  thumb=im.resize((320,320),Image.Resampling.LANCZOS);x=(n-1)%4*320;y=(n-1)//4*352;sheet.paste(thumb,(x,y),thumb);dr.text((x+8,y+322),f'{d}/{n:02} {frame["supportLeg"]} {frame["position"]}',fill=(15,20,25))
  checks.append({'file':frame['file'],'sha256':h,'nativeSource':meta['derivedFrom']['file'],'registrationInputSha':meta['registrationTransform']['inputSha256'],'pass':True})
 sheet.save(R/f'run/staging/south-bamboo-contact-{d}-formal-review.jpg',quality=96)
assert len(set(hashes))==32
report={'status':'technical_pass_static_pending_root_preview','frames':checks,'duplicates':0,'normalCycleMs':1200,'reviewScope':'Dimension/mode/hash/source/registration check only. Static visual separately in contact audits; actual playback belongs to root.'}
(R/'audit/south-contact-final-technical.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(checks),'duplicates':0,'status':report['status']}))


from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,numpy as np
PROD=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
batch=PROD/'donghai_batch_r08_c08_c10'
out=batch/'resume_audit_20260918'
out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[];errors=[]
for app in ('donghai_day','donghai_lantern'):
 root=PROD/app/'r08_c10'
 files=list((root/'native').glob('*.record.json'))
 if app=='donghai_day':files+=list((PROD/app/'r08_c08_c09_c10_joint/repairs_v1').glob('*/native.record.json'))
 for f in files:
  r=json.loads(f.read_text(encoding='utf8'));entry=dict(record=str(f),sha256=sha(f),id=r.get('id'),checks=[])
  for k,h in [('outputPath','outputSha256'),('sourceOutputPath','sourceOutputSha256'),('promptPath','promptSha256'),('guidePath','guideSha256'),('submittedReferencePath','submittedReferenceSha256')]:
   if k not in r:continue
   ok=Path(r[k]).exists() and sha(r[k])==r[h];entry['checks'].append(dict(field=k,ok=ok))
   if not ok:errors.append(str(f)+': '+k)
  for ref in r.get('actualInputReferences',[]):
   ok=sha(ref['path'])==ref['sha256'];entry['checks'].append(dict(field='actualInputReference',path=ref['path'],ok=ok))
   if not ok:errors.append(str(f)+': actual ref')
  with Image.open(r['outputPath']) as im:
   extrema=im.getchannel('A').getextrema() if 'A' in im.getbands() else (255,255)
   entry.update(pixels=list(im.size),alphaExtrema=list(extrema),nativeSizeCorrect=im.size==(1254,1254),fullyOpaque=extrema==(255,255))
   if im.size!=(1254,1254) or extrema!=(255,255):errors.append(str(f)+': size/alpha')
  checks.append(entry)
day=PROD/'donghai_day/r08_c08_c09_c10_joint/output_v3'
assembly=json.loads((day/'assembly.json').read_text())
outputChecks=[]
for e in assembly['outputs']:
 p=Path(e['file']);ok=sha(p)==e['sha256'] and list(Image.open(p).size)==e['pixels']
 outputChecks.append(dict(path=str(p),ok=ok,sha256=sha(p)))
 if not ok:errors.append(str(p))
core=np.array(Image.open(day/'core12288x4096.png'))
rejoin=np.concatenate([np.array(Image.open(day/f'r08_c{c:02d}.png')) for c in (8,9,10)],axis=1)
assert np.array_equal(core,rejoin)
old=PROD/'donghai_day/r08_c09/joined_pair/r08_c08.png'
assert np.array_equal(np.array(Image.open(day/'r08_c08.png')),np.array(Image.open(old)))
display=out/'display_native';display.mkdir(exist_ok=True)
views=[]
for p in sorted((day/'qa').glob('*.png')):
 if 'mask' in p.name:continue
 q=display/(p.stem+'.jpg')
 Image.open(p).convert('RGB').save(q,quality=96,subsampling=0)
 views.append(dict(source=str(p),sourceSha256=sha(p),display=str(q),pixels=list(Image.open(q).size),resized=False,displayEncoding='JPEG96; source preserved PNG'))
report=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),status='mechanical_pass_pending_current_visual_review' if not errors else 'failed',errors=errors,nativeRecords=checks,nativeRecordCount=len(checks),outputChecks=outputChecks,rejoinPixelIdentical=True,oldC08PixelIdentical=True,daySelected=str(day),displayViews=views)
(out/'mechanical-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(errors=errors,nativeRecords=len(checks),dayBase=16,dayRepairs=2,lanternBase=11,dayOutputs=len(outputChecks),displayViews=len(views),report=str(out/'mechanical-audit.json')),ensure_ascii=False))

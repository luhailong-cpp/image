from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
E=Path(__file__).resolve().parent;O=E/'child-selected';load=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=load(O/'audit.json');checked=[];seen=set()
for step in m['reconstructionSteps']:
 man=load(step['manifest']['file']);joined=man.get('joined');
 if not joined:continue
 gen=Path(joined['file']+'.generation.json')
 if not gen.exists():continue
 gr=load(gen)
 for source in gr.get('nativeSources',gr.get('derivedFrom',gr.get('sources',[]))):
  if not isinstance(source,dict) or not source.get('file'):continue
  p=Path(source['file'])
  if p.name!='native.png' or str(p) in seen:continue
  seen.add(str(p));assert sha(p)==source['sha256'];r=Path(str(p)+'.generation.json');assert r.exists();record=load(r)
  with Image.open(p) as im:size=list(im.size)
  assert size[0]>=1200 and size[1]>=1200
  assert record.get('actualModel') is None and record.get('actualQuality') is None
  checked.append(dict(file=str(p),sha256=sha(p),pixels=size,generationRecord=dict(file=str(r),sha256=sha(r)),actualModel=None,actualQuality=None,evidence=record.get('evidence'),route=record.get('route'),submittedParameters=record.get('submittedParameters')))
out=dict(checkedAt=datetime.now(timezone.utc).isoformat(),scope='New native AI sources for joined patches of11 post-v015 source reconstruction steps; prior baseline inherited from main audit.',imageCount=len(checked),images=checked,allSourcesNativeSized=True,modelAndQualityUndisclosed=True,mainAudit=dict(file=str(O/'audit.json'),sha256=sha(O/'audit.json')))
(O/'native-source-supplement.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'checkedNativeImages':len(checked),'supplement':str(O/'native-source-supplement.json')}))

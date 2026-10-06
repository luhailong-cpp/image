from pathlib import Path
import json, hashlib, shutil
from datetime import datetime, timezone
from PIL import Image
B=Path(__file__).resolve().parent
ROOT=Path('D:/work/image')
DAY=B.parent.parent/'lanxian_day/r09_c10'
NORTH=B.parent/'r08_c10'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def snap(source,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
 return {'source':str(source),'snapshot':str(dest),'sha256':sha(dest),'bytes':dest.stat().st_size}
assert sha(DAY/'selected/core4096.png')=='0cefa2ece52b708f6b7021bfa878d466451cc1a0fd337cc9679754e949686c8b'
assert sha(DAY/'selected/extended4326.png')=='9f4279c1fec0ff91aa62fcb21e2fcb3e78ca021266732ed6096adb9338e341f5'
d=json.loads((DAY/'selected/delivery.manifest.json').read_text(encoding='utf-8-sig'))
assert d['qualifiedComplete4KCandidate'] is True
assert sha(NORTH/'selected/core4096.png')=='4c5410f54c977ac9122f2ce5237306d070e872171b7639ba4f3a67fae8db8e22'
assert sha(NORTH/'selected/extended4326.png')=='356a3500b749eaa1fb3dab0f46c1a8b73f005c9dca0860b18847dd4f44345cdc'
records=[]
for label,src in [('day',DAY),('north-spring',NORTH)]:
 for name in ['core4096.png','extended4326.png']:
  records.append(snap(src/'selected'/name,B/'shared-geometry'/label/name))
 for p in src.rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.json','.txt','.md','.py','.ps1']:
   records.append(snap(p,B/'shared-geometry'/label/'evidence'/p.relative_to(src)))
write(B/'shared-geometry/provenance.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceReuse':'Exact qualified day shared geometry, not a new generation. North spring selected pinned only as neighbor evidence.','records':records,'readOnlySources':True})
write(B/'config-snapshot.json',json.loads((ROOT/'config/image-generation.json').read_text()))
write(B/'official-verification.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'release':'https://openai.com/index/introducing-chatgpt-images-2-5/','model':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','observations':['Release confirms Images 2.5 on ChatGPT, ChatGPT Work and Codex.','Model page identifies Sunburst as most capable image generation/editing model and supports max quality.'],'configurationUnchanged':True,'actualBuiltinModel':None,'actualBuiltinQuality':None,'reason':'Tool exposes neither selector nor returned version/quality.'})
core=Image.open(B/'shared-geometry/day/core4096.png').convert('RGB')
ext=Image.open(B/'shared-geometry/day/extended4326.png').convert('RGB')
(B/'inputs').mkdir(exist_ok=True)
core.crop((700,2800,1954,4054)).save(B/'inputs/southwest-cap1254.png')
core.resize((1254,1254),Image.Resampling.LANCZOS).save(B/'inputs/day-overview1254.png')
ext.crop((0,0,1254,1254)).save(B/'inputs/northwest1254.png')
print(json.dumps({'records':len(records),'status':d['status'],'outputs':list(d['outputs'])},ensure_ascii=False))

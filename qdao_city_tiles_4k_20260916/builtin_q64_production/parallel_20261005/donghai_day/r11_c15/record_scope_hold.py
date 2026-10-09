from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1];T=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[]
for p in sorted((T/'native').glob('r??_c??.png')):
 rec=Path(str(p)+'.generation.json');v=json.loads(rec.read_text())
 with Image.open(p) as im:
  im.load();assert im.size==(1254,1254)
 assert v['sha256']==sha(p) and v['actualModel'] is None and v['actualQuality'] is None and not v['finalArtUpscaled']
 assert sha(v['prompt'])==v['promptSha256']
 for x in v['references']:assert sha(x['file'])==x['sha256']
 items.append(dict(file=str(p),sha256=sha(p),record=str(rec),recordSha256=sha(rec),pixels=[1254,1254],producerActualViewed=True,visualScope='single native fragment geometry and material review; no assembled seam acceptance'))
assert len(items)==10
plan=json.loads((T/'plan.json').read_text())
assert plan['neighbors']['north']['bindingStatus']=='pending'
assert not list((T/'native').glob('r01_*.png'))
for v in plan['externalNativeBindings']:
 assert sha(v['file'])==v['sha256'] and sha(v['record'])==v['recordSha256']
now=datetime.now(timezone.utc).isoformat()
report=dict(createdAtUtc=now,tile='r11_c15',status='held-pending-user-scope-verification',directionSource='parent root instructed immediate halt of old16x16 expansion while user scope is verified',newGenerationInFlight=False,canonicalOutputAvailable=False,countsAsCompleteTile=False,formalAccepted=False,globalRect=plan['globalRect'],worldRect=plan['worldRect'],nativePatches=items,nativeCount=10,missingNativeNames=[f'r{rr:02}_c{cc:02}' for rr in range(1,5) for cc in range(1,5) if not (T/'native'/f'r{rr:02}_c{cc:02}.png').exists()],northBindingPending=True,topRowGenerated=False,readyButNotGenerated=dict(name='r03_c04',guide=str(T/'guides/r03_c04.png'),guideSha256=sha(T/'guides/r03_c04.png'),actualViewed=True,prompt=str(T/'prompts/r03_c04.txt'),imagegenCalled=False),reusableAssets=[dict(file=str(T/'guides/local-layout.png'),sha256=sha(T/'guides/local-layout.png'),role='confirmed geometry reference-only crop, never finalHD pixels'),dict(file=str(T/'guides/local-structure.png'),sha256=sha(T/'guides/local-structure.png'),role='native1254 local structure reference-only, actual viewed, not whole4K final')],externalEastNativeBindings=plan['externalNativeBindings'],rejectedAttempts=['qa/r04_c01-rejected-raised-waterline.generation.json','qa/r04_c02-rejected-raised-waterline.generation.json'],rejectedRasterAvailability='Initial two attempts were deleted before halt after explicitly failing shape/waterline review; historical text includes exact prompt/config/source evidence. No further image cleanup during scope hold.',scopeLimitation='All raw native sources, references, prompts and neighbor intersection records retained for reuse after scope confirmation. No final assembly, internal seam QA or complete tile acceptance has been performed.')
(T/'scope-hold-status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name in ['progress.json','current-work.json']:
 p=T/name;v=json.loads(p.read_text());v.update(phase='held-pending-user-scope-verification',updatedAtUtc=now,nativePatchesSaved=10,newGenerationInFlight=False,nextAction='Await verified revised scope before more generation or assembly');p.write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(dict(nativeCount=10,report=str(T/'scope-hold-status.json'),reportSha256=sha(T/'scope-hold-status.json'),missing=report['missingNativeNames'])))


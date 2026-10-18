from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=p.as_posix(),sha256=sha(p))
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
base=Z/'tiles/r03_c01_candidate-v11_4096.png';record=base.with_suffix('.native-repair.json');coverage=Z/'qa/r03_c01_v11_internal33_coverage_connected_20261016.json';strict=Z/'qa/r03_c01_v11_strict_native_replay_20261016.json';c=read(coverage);s=read(strict)
assert c['candidate']['sha256']==sha(base) and c['record']['sha256']==sha(record)
assert c['geometryPassedCount']==c['materialPassedCount']==c['nativeCropCount']==33 and c['internalClosurePassed'] is True
assert s['status']=='base_native_coverage_reverified' and s['base']['sha256']==sha(base) and s['proof']['verifiedPixelCount']==16777216 and s['proof']['fullNativeCoverage'] is True
d=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),tileId='r03_c01',candidate=info(base),record=info(record),internal33Coverage=info(coverage),strictNativeReplay=info(strict),outer115Delta=info(Z/'qa/r03_c01_v11_internal_review/outer115_delta.json'),rootMaskReviews=[info(Z/'qa/r03_c01_first4_masks_root_review_20261016.json'),info(Z/'qa/r03_c01_second4_masks_root_review_20261016.json'),info(Z/'qa/r03_c01_v11_internal_review/middle_cliff_root_independent_review.json')],nativePixelCountVerified=16777216,selectedCoreCount=16,internalGeometryClosurePassed=True,internalMaterialClosurePassed=True,internalClosurePassed=True,internalPassScope='33 standard internal native seam/junction crops plus local native repair masks; not whole-zone or neighbouring tile acceptance',formalAccepted=False,wholeZoneComplete=False,route='builtin image_gen; exact native-coordinate mechanical source selection',actualModel=None,modelEvidence='Builtin image tool did not disclose model. No paid API route used.',remaining=['Cross-tile and full-zone visual acceptance pending; north and west water boundary changed from v1, south/east115 unchanged.'])
p=Z/'qa/r03_c01_v11_internal_closure_20261016.json'
with p.open('x',encoding='utf8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
statepath=Z/'root-current-selection-20261012.json';state=read(statepath);entry=state['tiles']['r03_c01'];entry.update(candidate=info(base),record=info(record),internalClosure=info(p),internalReview=info(coverage),internalGeometryClosurePassed=True,internalMaterialClosurePassed=True,internalClosurePassed=True,materialStatus='INTERNAL_PASS',formalAccepted=False,internalPassScope=d['internalPassScope'],repairStatus='33/33 internal native crops and strict 16777216 pixel provenance PASS. Cross-tile and whole-zone acceptance pending.');state['updatedAtUtc']=d['createdAtUtc'];statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(info(p)))

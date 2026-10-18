from pathlib import Path
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016');sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
ref=lambda f:{'file':str(f),'sha256':sha(f)}
files=['trial01-upper.png','trial01-lower.png','trial01-upper-left.png','trial01-right.png','trial01-left.png','trial01-bottom.png','trial01-bottom-exterior.png','trial01-full-context.png','v2-hardware.png','v2-north.png','v2-south.png','v2-west.png','v2-east.png','v2-lower.png','v2-bottom.png']
data={'reviewer':'root','actuallyViewed':True,'formalAccepted':False,'status':'passed_local_native_adoption','proposal':ref(D/'adoption-proposal.json'),'existingSourcePatch':ref(D/'red-arc-existing-source-proposal.json'),'viewedCrops':[ref(D/f) for f in files],'finding':'Row2 upper/lower paving joints and complete branch endpoints join cleanly; local perimeter and outside-south context pass. Old detached red arc was present in baseline and not introduced by new paving mask. Existing same-world s03_02 native halo removes only 1235 background pixels above the original unchanged complete red ball cap; seven v2 crops actually viewed and pass. Requires combined incremental candidate review; coping and wood style remain pending.'}
(D/'root-review-v2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(ref(D/'root-review-v2.json'))


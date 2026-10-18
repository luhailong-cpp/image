from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12');q=p/'qa/repair-m05-20261016'
h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
r={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r08_c12','issue':'M05','status':'unpassed-deferred-after-two-local-repairs','repairAttempts':2,'viewedNativeComposites':['m05-composed-v1.png','m05-composed-v2.png'],'findings':[{'version':1,'result':'Central vertical joint repaired, but horizontal discontinuity remains at left and new diagonal joint offsets occur at right and bottom paste boundaries.'},{'version':2,'result':'Interior grid is continuous, but left, right and bottom crop boundaries have larger phase changes; perimeter pixels are not preserved. No usable improvement at actual native paste boundary.'}],'bestWorkingRepair':'candidates/r08_c12.m05-v20261016.png','bestWorkingRepairSha256':h(p/'candidates/r08_c12.m05-v20261016.png'),'adoptedCandidateUnchanged':True,'adoptedCandidate':'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png','adoptedCandidateSha256':'e231be2f8e985a46055fda85817abf6a5340b80d92d754a981054e8a3d1152ea','next':'Defer M05; generate independent missing r07_c12 from unchanged south/east edge. No third repair at this point.','internalPassed4kCount':0,'formalAcceptedCount':0,'actualModel':None,'paidApi':False}
(q/'review-v20261016.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=p/r['adoptedCandidate'];dst=p/'candidates/r08_c12-native-4096-v20261016.png';assert not dst.exists();shutil.copy2(src,dst)
pr=p/'tile-progress.json';v=json.loads(pr.read_text());v.update(lastReview=str(q/'review-v20261016.json'),lastSavedNative='native/repairs/m05-joints-v2-20261016.png',workingRepairCandidate=str(p/r['bestWorkingRepair']),workingRepairCandidateSha256=r['bestWorkingRepairSha256'],workingRepairCandidateStatus='unpassed-deferred-after-two-local-repairs',candidate=str(dst),candidateSha256=h(dst),updatedAt=r['createdAt'])
pr.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidate':str(dst),'sha256':h(dst),'status':r['status']}))


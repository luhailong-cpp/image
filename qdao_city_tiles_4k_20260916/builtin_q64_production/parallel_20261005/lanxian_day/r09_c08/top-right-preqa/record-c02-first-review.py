from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08')
Q=T/'ready-cell-qa/r01_c02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((Q/'manifest.json').read_text());d=json.loads((Q/'north-detail/manifest.json').read_text())
views=[]
for entry in m['checks']+d['scopes']:
 assert sha(Path(entry['file']))==entry['sha256']
 views.append({'file':entry['file'],'sha256':entry['sha256'],'actualView':True})
report={'createdAt':datetime.now(timezone.utc).isoformat(),'reviewer':'c08_remaining_top','cell':'r01_c02','nativeSha256':'aee6d1245cff2f953dc965dff267ac747083dee1ccffcc7d0d5c04f7bd68d2ea','viewedScopes':views,'actualScopeViews':7,'nativeOutputAlsoViewed':True,'standardScopeResults':{'external_north':'failed_actionable','internal_east':'no_actionable_defect_seen','east_guide_transition':'no_actionable_defect_seen'},'findings':[{'scope':'north-detail/orange-rim.png','finding':'At source north-board y256 (detail y60), orange planter rim contour jumps sideways by several pixels with a transverse material step.'},{'scope':'north-detail/wood-board.png','finding':'At source y256 (detail y60), a straight horizontal shade boundary crosses the brown wooden backboard and its diagonal joint.'},{'scope':'north-detail/stone-post.png','finding':'At source y256 (detail y80), bench upright and stone shaft edges have small position discontinuities; upper/lower material tones differ.'},{'scope':'north-detail/foliage.png','finding':'At source y256 (detail y80), the canopy and adjacent stone panel show a straight horizontal darker band/color break.'}],'interpretation':'Mixed geometry endpoint drift and material tone discontinuity between true north source and regenerated south. Broad overview masked defects; focused native crops are decisive.','accepted':False,'formalAccepted':False,'clientValidated':False,'wholeTileReviewed':False,'nextDependency':'Do not treat this r01_c02 candidate as qualified or prepare r01_c01 until root chooses repair/continuation.'}
(Q/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'review':str(Q/'review.json'),'sha256':sha(Q/'review.json')}))


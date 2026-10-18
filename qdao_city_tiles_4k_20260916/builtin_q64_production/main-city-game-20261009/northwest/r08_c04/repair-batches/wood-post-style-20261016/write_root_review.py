from pathlib import Path
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/wood-post-style-20261016');sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();ref=lambda f:{'file':str(f),'sha256':sha(f)}
d={'status':'passed_local_native_adoption','reviewer':'root','actuallyViewed':True,'formalAccepted':False,'proposal':ref(D/'adoption-proposal.json'),'source':ref(D/'native.png'),'crops':[ref(D/f) for f in ['post-full.png','top.png','left.png','right.png','bottom-edge.png']],'finding':'Actual five crops reviewed. Wood uses smooth, fine hand-painted chibi brown material and simplified growth rings, same cylinder silhouette and lighting. Native-only mask perimeter along top/left/right stays coherent with current stone context. Selected pixels stop at tile south boundary; unselected old source halo does not prove any south neighbor continuity. This passes only local wood-material correction; remaining coping geometry and broader stone style are not upgraded.'}
(D/'root-review.json').write_text(json.dumps(d,indent=2))
print(ref(D/'root-review.json'))
q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-25-source-incremental-20261016T131854187430Z-707a552b42438c12/full-audit-reviewed-status.json')
m=json.loads(q.read_text()); print(json.dumps([{'name':c['name'],'file':c['file'],'status':c['status']} for c in m['crops'] if c['name'] in m['changedCropNames']],indent=2))


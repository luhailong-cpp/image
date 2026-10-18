from pathlib import Path
import json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/qa/native-25-source-incremental-20261016T131854187430Z-707a552b42438c12')
m=json.loads((D/'full-audit-reviewed-status.json').read_text());sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
crops=[]
for c in m['crops']:
 if c['name'] in m['changedCropNames']:
  assert sha(c['file'])==c['sha256'];crops.append({k:c[k] for k in ['name','file','sha256','pixelKey']})
for c in crops:c.update({'status':'passed','actuallyViewed':True,'finding':'Root actually viewed at native crop scale; stone joint endpoints are continuous, red cap has no detached arc, and changed seam/junction perimeter is coherent.'})
assert len(crops)==8
r={'reviewer':'root','actuallyViewed':True,'formalAccepted':False,'candidate':m['candidate'],'baseManifest':{'file':str(D/'full-audit-reviewed-status.json'),'sha256':sha(D/'full-audit-reviewed-status.json')},'crops':crops,'unchangedReviewsReused':32,'remainingFailedCrop':'internal-x3072-segment04','scope':'25-source changed crops only; coping and bottom material/style not accepted'}
(D/'root-review-overlay.json').write_text(json.dumps(r,indent=2));print({'file':str(D/'root-review-overlay.json'),'sha256':sha(D/'root-review-overlay.json')})


from pathlib import Path
from datetime import datetime,timezone
import sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08/repair-batches/blue-glaze-cross-20261017-fix03');Q=T/'qa/native17-glaze-repair-20261017-v1';m=p.read(Q/'manifest.json')
reviews=[]
bad={'west_seg3','west_joint2048'}
for c in m['crops']:
 if c['reusedPixelIdentical']:reviews.append(dict(name=c['name'],file=c['file'],sha256=c['sha256'],kind=c['kind'],status=c['status'],actuallyViewed=False,reusedPixelIdentical=True,evidence=c['reusedReview']))
 else:reviews.append(dict(name=c['name'],file=c['file'],sha256=c['sha256'],kind=c['kind'],status='needs_repair' if c['name'] in bad else 'passed',actuallyViewed=True,reusedPixelIdentical=False,finding='West fixed neighbor remains darker at tile x0 along lowest blue glaze surface; vertical tonal transition remains visible. Not passed.' if c['name'] in bad else 'Actual native changed crop viewed. Lowest roof glaze is continuous across the former horizontal split; tile rims, cast shadow and red timber align. Additional x1024 crossing and mask joins retain continuity.'))
counts={kind:{s:sum(c['kind']==kind and c['status']==s for c in reviews) for s in ['passed','needs_repair']} for kind in ['internal','external']}
r=dict(recordedAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='/root/resume_r06_c08_20261017',candidate=m['candidate'],cropReviews=reviews,counts=counts,totalCount=42,pixelHashReusedCount=34,newActuallyViewedCount=8,localMaskPerimeterActuallyViewed=True,localMaskPerimeterFile=str(B/'qa-v1/local-composite.png'),localMaskPerimeterSha256=p.sha(B/'qa-v1/local-composite.png'),internalQAPassed=True,formalAccepted=False,unavailableExternal=m['unavailableExternal'],pending=list(sorted(bad)))
p.write_json(Q/'reviewed-status.json',r,replace=False)
p.write_json(B/'adoption-review.json',dict(status='adopted_internal_improvement_external_pending',reviewer='/root/resume_r06_c08_20261017',sourceSha256=p.sha(B/'native.png'),maskSha256=p.sha(B/'mask-v1.png'),selectedNativePixelCount=158167,sourcePixelsResampled=False,sourcePixelsBlended=False,sourcePixelsRecolored=False,internalHorizontalToneIssueResolved=True,westernVerticalToneIssueResolved=False,formalAccepted=False,candidate=m['candidate'],qa=dict(file=str(Q/'reviewed-status.json'),sha256=p.sha(Q/'reviewed-status.json'))),replace=False)
checkpoint=dict(recordedAtUtc=datetime.now(timezone.utc).isoformat(),tile='r06_c08',selectedCoreCount=16,sourceCount=17,completeCandidateProduced=True,candidate=m['candidate'],candidateManifest=str(T/'candidate/native17-glaze-repair-20261017-v1/manifest.json'),sameWorldNativePixels=16777216,qaReview=dict(file=str(Q/'reviewed-status.json'),sha256=p.sha(Q/'reviewed-status.json')),counts=counts,internalQAPassed=True,formalAccepted=False,actualModel=None,route='builtin',pending=list(sorted(bad)),unavailableExternal=m['unavailableExternal'],nextStep='Await r05_c08 s04_04 real selected core and check only new north cuts. West vertical tone strip remains needs_repair after concentrated native correction; keep best candidate and precise issue, no formal/whole-map acceptance.')
p.write_json(T/'resume-checkpoint-20261017-v03.json',checkpoint,replace=False)
print({'counts':counts,'reviewSha256':p.sha(Q/'reviewed-status.json'),'checkpointSha256':p.sha(T/'resume-checkpoint-20261017-v03.json')})


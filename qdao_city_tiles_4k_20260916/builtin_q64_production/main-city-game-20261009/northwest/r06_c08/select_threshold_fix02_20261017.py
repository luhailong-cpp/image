from pathlib import Path
import sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
D=T/'qa/source-review/s04_04_fix02';m=p.read(D/'manifest.json')
note='Native fix corrects wall bottom: gray floor continues from west at source y1105 and wooden jamb terminates on it; foreground gold/red silhouette retained. Full source plus north, west and NW exact native crops actually viewed and passed. Whole tile QA and unavailable exterior edges still pending.'
p.write_json(D/'review.json',dict(source=m['source'],reviewer='/root/resume_r06_c08_20261017',actuallyViewed=True,status='passed_available_local_neighbors',cropReviews=[dict(file=c['file'],sha256=c['sha256'],actuallyViewed=True,status='passed',finding=note) for c in m['crops']],finding=note,formalAccepted=False,fullTileInternalQAPassed=False),replace=False)
print(p.record_selection('r06_c08','s04_04','s04_04_fix02',note,str(D/'review.json')))
p.write_json(T/'pending/s04_04-fix02-resolution-20261017.json',dict(status='resolved_available_local_crop',supersedes='s04_04_fix01.json',source=m['source'],finding=note,formalAccepted=False),replace=False)
Q=T/'qa/partial15-restart-20261017';q=p.read(Q/'manifest.json');reviews=[]
for c in q['crops']:
 prior=c['matchingPriorReviews'];assert prior
 bad=[r for r in prior if r['status']=='needs_repair']
 reviews.append(dict(file=c['file'],sha256=c['sha256'],name=c['name'],status='needs_repair' if bad else 'passed',actuallyViewed=False,reusedActualVisualReview=True,reuseBasis='Exact RGB pixel hash matches prior actually viewed crop with verified file SHA',evidence=bad or prior))
p.write_json(Q/'reviewed-status.json',dict(selectedCount=15,checkpointOnly=True,sourceSelectionBeforeS04_04Fix02=True,reviewedBy='prior actual visual reviews reused by /root/resume_r06_c08_20261017',cropReviews=reviews,passed=sum(r['status']=='passed' for r in reviews),needsRepair=sum(r['status']=='needs_repair' for r in reviews),missingInternalCrops=3,formalAccepted=False),replace=False)


from pathlib import Path
import sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
D=T/'qa/source-review/s03_01_fix02';m=p.read(D/'manifest.json')
issue='Second native correction substantially reduces the cyan rectangle. Small remaining vertical blue-glaze tone boundary at west x0,y2048..2120 and subtle top strip transition remain needs_repair, not passed. Tile/beam geometry unchanged; east/south joints checked healthy. Deferred after two local repair calls while final independent missing core is completed.'
bad={'west-seam','northwest-junction','north-seam'}
review=dict(source=m['source'],reviewer='/root/resume_r06_c08_20261017',actuallyViewed=True,status='selected_with_local_issue',cropReviews=[dict(file=c['file'],sha256=c['sha256'],actuallyViewed=True,status='needs_repair' if c['name'] in bad else 'passed',finding=issue if c['name'] in bad else 'Actual native crop viewed; crossing geometry and material remain coherent.') for c in m['crops']],finding=issue,formalAccepted=False,fullTileInternalQAPassed=False)
p.write_json(D/'review.json',review,replace=False)
p.write_json(T/'pending/s03_01_fix02.json',dict(status='needs_repair',selected=True,issue=issue,affectedTileLTRB=[0,2048,1024,2130],propagationEdgesHealthy=['east','south'],attemptsThisBatch=['s03_01_fix01','s03_01_fix02']),replace=False)
print(p.record_selection('r06_c08','s03_01','s03_01_fix02',issue,str(D/'review.json')))


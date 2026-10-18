from pathlib import Path
import sys
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
D=T/'qa/source-review/s01_04_native01';m=p.read(D/'manifest.json')
note='Filled final core from exact west s01_03_fix03 and south s02_04 plus southwest s02_03 native anchors. Whole source and all three actual west/south/SW crops viewed; curved teal courses, eave, hanging bracket and gold scroll continue coherently. No north source existed at generation; north exterior remains unreviewed and must be matched by its owner.'
p.write_json(D/'review.json',dict(source=m['source'],reviewer='/root/resume_r06_c08_20261017',actuallyViewed=True,status='passed_available_local_neighbors',cropReviews=[dict(file=c['file'],sha256=c['sha256'],actuallyViewed=True,status='passed',finding=note) for c in m['crops']],finding=note,formalAccepted=False,fullTileInternalQAPassed=False),replace=False)
print(p.record_selection('r06_c08','s01_04','s01_04_native01',note,str(D/'review.json')))


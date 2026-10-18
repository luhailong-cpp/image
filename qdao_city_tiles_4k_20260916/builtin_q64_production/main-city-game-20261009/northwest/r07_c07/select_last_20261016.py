from pathlib import Path
import sys,json
T=Path(__file__).resolve().parent
sys.path.insert(0,str(T.parent))
import production_v2 as p
D=T/'qa/source-review/s01_01_native03'
m=p.read(D/'manifest.json')
reviews=[]
for c in m['crops']:
 pending=c['name'] in ('south-seam','southeast-junction')
 reviews.append(dict(file=c['file'],sha256=c['sha256'],status='needs_repair' if pending else 'passed',finding='At y1024 the vertical stone strips are shifted; dark coursed stone changes abruptly to pale flat stone. Requires a physical aligned junction.' if pending else 'Actually viewed at native scale; corresponding edge/architecture continues.'))
p.write_json(D/'review.json',dict(reviewer='/root/continue_r07_c07',actuallyViewed=True,cropReviews=reviews,status='needs_local_south_stone_alignment',formalAccepted=False,fullTileInternalQAPassed=False),replace=False)
print(p.record_selection('r07_c07','s01_01','s01_01_native03','Best current native source; north/west/east geometrically stable, south stone/jamb junction pending repair.',str(D/'review.json')))


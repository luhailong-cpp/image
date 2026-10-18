"""Record actual visual observations for an existing immutable quick evidence set."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
tile,pid,label,note=sys.argv[1:5]
assert tile in ('r13_c12','r14_c12')
Q=Z/tile/'qa'/('quick-'+pid+'-'+label)
m=json.loads((Q/'manifest.json').read_text())
for r in m['evidence']:
 assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
out=Q/'visual-review.json'; assert not out.exists()
out.write_text(json.dumps(dict(createdAt=datetime.now(timezone.utc).isoformat(),reviewer='/root/east_water_finish_20261016',tile=tile,patch=pid,viewedNativeEvidence=m['evidence'],observations=note,geometryStatus='provisional_continuity_observed',materialStatus='pending_full_tile_review',formalAccepted=False),ensure_ascii=False,indent=2),encoding='utf8')
print(str(out))

from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
def pin(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
entries=[]
for r in [1,4]:
 s=f'r03_c01_s{r:02d}_04_a01'
 entries.append({'stem':s,'image':pin(Z/'native'/f'{s}.png'),'rightPair':pin(Z/'qa/r03_c01_first2_quickcheck_20261016'/f'{s}_right_pair.png'),'result':'quick_layout_and_right_neighbor_geometry_PASS','observations': 'Viewed full1254 native and unresampled700x1024 right-boundary pair. Rock faces, flower groups, water foam continue across boundary.' if r==1 else 'Viewed full1254 native and unresampled700x1024 right-boundary pair. Courtyard paving, cream carved railing and flowers continue across boundary without material step.'})
out=Z/'qa/r03_c01_first2_quickcheck_20261016/review.json'
assert not out.exists()
out.write_text(json.dumps({'reviewer':'root','timestamp':datetime.now(timezone.utc).isoformat(),'sourceNeighbor':pin(Z/'tiles/r03_c02_candidate-v7_4096.png'),'entries':entries,'internal33Checked':False,'formalAccepted':False},indent=2)+'\n')
print(pin(out))

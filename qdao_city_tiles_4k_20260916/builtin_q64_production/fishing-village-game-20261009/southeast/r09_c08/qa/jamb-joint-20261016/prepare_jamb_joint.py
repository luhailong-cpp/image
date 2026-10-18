from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
Q=Path(__file__).resolve().parent;Z=Q.parents[2];sys.path.insert(0,str(Z))
from review_external_seams import Sources
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected={'r09_c08':('p44','5c3896b829f0b55d99fc589cdfa64e8fdc137479f2aa2ac31df1a973920fb8bc'),'r10_c08':('p14','495536017d01bd3c3c6783129edda1f85a9e55ab71c91db8df5cbdef6e7d4a45')}
targets={}
for tile,(pid,h) in expected.items():
 sel=Z/tile/'selected-patches.json';j=json.loads(sel.read_text(encoding='utf-8-sig'));p=Z/tile/j['patches'][pid]
 assert sha(p)==h,(tile,'selected source mismatch')
 targets[tile]={'patch':pid,'file':str(p),'sha256':h,'selection':str(sel),'selectionSha256':sha(sel)}
box=[31744,36065,32998,37319];im,pieces,missing=Sources().extract(box);assert not missing,missing
p=Q/'jamb-input-v1-1254.png';assert not p.exists();im.save(p)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'frameGlobalBox':box,'image':str(p),'sha256':sha(p),'sources':pieces,'targetPatches':targets,'seamYInFrame':799,'scope':'Right window wooden jamb surface only. Preserve single diamond flower, all window/post/roof silhouettes, and bracket.','operation':'Exact selected core pixels; no resampling or image synthesis.'}
(Q/'jamb-input-v1.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'image':str(p),'sha256':sha(p),'targets':targets}))

from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
Q=Path(__file__).resolve().parent; Z=Q.parents[2];sys.path.insert(0,str(Z))
from review_external_seams import Sources
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
box=[31744,36065,32998,37319]
s=Sources();im,pieces,missing=s.extract(box);assert not missing,missing
p=Q/'joint-input-v1-1254.png';assert not p.exists();im.save(p)
sources={}
for tile,pid in [('r09_c08','p44'),('r10_c08','p14')]:
 sel=Z/tile/'selected-patches.json';j=json.loads(sel.read_text(encoding='utf-8-sig'));n=Z/tile/j['patches'][pid]
 sources[tile]={'patch':pid,'file':str(n),'sha256':sha(n),'selection':str(sel),'selectionSha256':sha(sel)}
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'frameGlobalBox':box,'dimensions':[1254,1254],'image':str(p),'sha256':sha(p),'sources':pieces,'targetPatches':sources,'seamYInFrame':799,'operation':'Selected native cores only, exact same coordinates, no scaling, blending, blur or synthesized geometry.','scope':'One window lattice jointly across north and south cores; retain bracket, posts, lantern and existing surrounding architecture.','formalAccepted':False}
(Q/'joint-input-v1.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'image':str(p),'sha256':sha(p),'sources':sources}))

from pathlib import Path
import json,hashlib,sys
from PIL import Image
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
sys.path.insert(0,str(ROOT/"tools"))
import finalize_scoped as f
old="0bbb59af2bb936e4d27945ea77240a56f0d34d4f887a24e4664c4ceb7d6a9e8c"
ctx=f.context("r10_c14",old)
a=f.requirements(ctx)
new=dict(ctx,image=Image.open(D/"v2-proposal-candidate.png").convert("RGB"))
b=f.requirements(new)
rows=[]
for k in a:
 x,y=a[k]["image"].convert("RGB"),b[k]["image"].convert("RGB")
 same=x.size==y.size and x.tobytes()==y.tobytes()
 rows.append(dict(file=str(a[k]["path"]),pixelsUnchanged=same,beforePixelSHA256=hashlib.sha256(x.tobytes()).hexdigest(),afterPixelSHA256=hashlib.sha256(y.tobytes()).hexdigest()))
report=dict(sourceCandidate=ctx["references"]["current"],proposal=f.ref(D/"v2-proposal-candidate.png"),scope="Read-only exact 28 required QA regeneration in memory; not visual approval.",items=rows,changedQA=[r["file"] for r in rows if not r["pixelsUnchanged"]],total=len(rows),candidateUnchanged=f.sha(ctx["candidate"])==old)
f.write(D/"v2-qa-impact.json",report)
print(json.dumps(dict(total=report["total"],changed=report["changedQA"],candidateUnchanged=report["candidateUnchanged"])))


from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;C=R.parent;S=C.parent.parent;B=S.parent.parent;Q=R/"baseline";Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cw=json.loads((S/"continuation_20261004/current-work.json").read_text())
items={v["tile"]:v["candidate"] for v in cw["workingCandidates"]}
paths={
 "r08_c07":S/"completion_20261004/c07/tone-candidate-v1/r08_c07.png",
 "r08_c08":C/"final-pair/r08_c08.png",
 "r08_c09":S/"completion_20261004/c09/tone-candidate-v1/r08_c09.png",
 "r09_c07":B/items["r09_c07"]["file"],
 "r09_c08":C/"final-pair/r09_c08.png",
 "r09_c09":S/"continuation_20261004/c09-pair-v2/r09_c09.png"}
a={};binding={}
for k,p in paths.items():
 im=Image.open(p).convert("RGB");assert im.size==(4096,4096);a[k]=np.array(im);binding[k]={"file":str(p),"sha256":sha(p),"pixels":[4096,4096]}
edges=[]
for row in [8,9]:
 for l,r in [(7,8),(8,9)]:
  left=f"r{row:02d}_c{l:02d}";right=f"r{row:02d}_c{r:02d}";key=left+"__"+right
  strip=np.concatenate([a[left][:,-192:],a[right][:,:192]],axis=1)
  board=np.concatenate([strip[i*1024:(i+1)*1024].transpose(1,0,2) for i in range(4)],axis=0)
  Image.fromarray(board).save(Q/(key+"-full.png"))
  edges.append({"id":key,"left":binding[left],"right":binding[right],"nativeBoard":str(Q/(key+"-full.png")),"boardLayout":"four consecutive1024px y segments transposed and stacked; shared seam centered row192 in each384px panel"})
for c in [7,8]:
 tl=a[f"r08_c{c:02d}"][-627:,-627:];tr=a[f"r08_c{c+1:02d}"][-627:,:627];bl=a[f"r09_c{c:02d}"][:627,-627:];br=a[f"r09_c{c+1:02d}"][:627,:627]
 im=np.concatenate([np.concatenate([tl,tr],axis=1),np.concatenate([bl,br],axis=1)],axis=0);Image.fromarray(im).save(Q/f"corner-r08r09-c{c:02d}c{c+1:02d}.png")
(R/"bindings.json").write_text(json.dumps({"sources":binding,"edges":edges,"scope":"current exact source-bound four vertical joins and two row8/9 four-tile junctions","formalAccepted":False},indent=2),encoding="utf-8")
print(json.dumps(binding,indent=2))

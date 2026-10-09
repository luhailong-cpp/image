from pathlib import Path
import json,hashlib,sys
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent
sys.path.insert(0,str(R/"tools/multi_edge"));import engine
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
v=D/"stage2-bounded";d=v/"standard-qa";d.mkdir(exist_ok=False);e=v/"r10_c12-proposal.png";old=T/"output/r10_c12.png";n=Path(read(T/"output/manifest.json")["northSource"])
current=list(engine.qa_images(Image.open(e).convert("RGB"),{"north":Image.open(n).convert("RGB")},"NW",256))
before={name:im for name,im,op,s in engine.qa_images(Image.open(old).convert("RGB"),{"north":Image.open(n).convert("RGB")},"NW",256)}
items=[]
for name,im,op,sources in current:
 p=d/(name+".png");im.save(p);same=np.array_equal(np.asarray(im),np.asarray(before[name]));item=dict(**ref(p),operation=op,sources=[ref(e)]+([ref(n)] if "north" in sources else []),nativeScale=1,actuallyViewed=False,identicalToOldCanonicalReconstruction=bool(same),oldCanonical=ref(old));write(str(p)+".generation.json",item);items.append(item)
# Exact true4-context junction using pending west p14 only where the full W tile is not yet available.
w=v/"p14-proposal.png";nw=Path(read(R/"r10_c11/plan.json")["northCandidate"]);q=Image.new("RGB",(320,320));ops=[(nw,[3936,3936,4096,4096],[0,0]),(n,[0,3936,160,4096],[160,0]),(w,[979,115,1139,275],[0,160]),(e,[0,0,160,160],[160,160])]
for p,box,xy in ops:q.paste(Image.open(p).crop(box),xy)
p=v/"qa-true-four-image-corner.png";q.save(p);write(str(p)+".generation.json",dict(**ref(p),operation=[dict(source=ref(src),cropLTRB=box,pasteXY=xy) for src,box,xy in ops],nativeScale=1,actuallyViewed=False,westIsUnapprovedP14Proposal=True,wholeWTileUnavailable=True))
write(d/"index.json",dict(candidate=ref(e),currentSource=ref(old),items=items,changedItems=[x["file"] for x in items if not x["identicalToOldCanonicalReconstruction"]],allRequireEitherActualReviewOrExplicitExactReuse=True,automaticVisualPass=False))
print(json.dumps(dict(total=len(items),changed=[Path(x["file"]).name for x in items if not x["identicalToOldCanonicalReconstruction"]])))


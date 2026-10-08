from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
m=json.loads((D/"mapping.json").read_text());C=Path(m["candidate"]["file"]);assert sha(C)==m["candidate"]["sha256"]
base=Image.open(D/"input-original.png").convert("RGBA");host=Image.open(D/"host-result.png").convert("RGBA")
core=np.array(Image.open(D/"replacement-mask.png"))>0
yy,xx=np.indices(core.shape)
dist=np.full(core.shape,1254.0)
poly=m['localRepairPolygon']
for (x1,y1),(x2,y2) in zip(poly,poly[1:]+poly[:1]):
 vx,vy=x2-x1,y2-y1
 t=np.clip(((xx-x1)*vx+(yy-y1)*vy)/(vx*vx+vy*vy),0,1)
 dist=np.minimum(dist,np.sqrt((xx-x1-t*vx)**2+(yy-y1-t*vy)**2))
dist[core]=0
# Exact host-pixel compositing only. A 40-pixel cosine return is allowed solely
# on existing wall, above the existing dock outline and right of the post.
a=(1+np.cos(np.minimum(dist,40)*np.pi/40))/2
yy,xx=np.indices(core.shape)
a[(xx<552)|(yy>937-0.5*xx)]=0
alpha=Image.fromarray(np.rint(a*255).astype(np.uint8),"L")
alpha.save(D/"v2-composite-alpha.png")
f=base.copy();f.paste(host,(0,0),alpha);f.save(D/"v2-proposal-frame.png")
candidate=Image.open(C).convert("RGBA");proposal=candidate.copy();proposal.paste(host,m["localOrigin"],alpha);proposal.save(D/"v2-proposal-candidate.png")
diff=np.any(np.array(candidate)!=np.array(proposal),axis=2);ys,xs=np.where(diff)
checks=dict(changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],changedPixelCount=int(diff.sum()),candidateUnchanged=sha(C)==m["candidate"]["sha256"],generatedArtSource=dict(file=str(D/"host-result.png"),sha256=sha(D/"host-result.png")),operation="Native aligned AI image alpha composite. Existing repair core opaque, cosine alpha return extends at most 40 pixels into existing wall only; excluded post/wood/water. No geometry warp, resampling, or algorithmic art drawing.",alpha=dict(file=str(D/"v2-composite-alpha.png"),sha256=sha(D/"v2-composite-alpha.png")),proposal=dict(file=str(D/"v2-proposal-candidate.png"),sha256=sha(D/"v2-proposal-candidate.png")),approved=False)
for n,box in [("v2-qa-detail.png",[560,2510,1230,3130]),("v2-qa-wall-post-joint.png",[740,2640,1020,2970]),("v2-qa-repair-surround.png",[680,2570,1140,3080])]:
 out=D/n;proposal.crop(box).save(out);write(D/(n+".generation.json"),dict(file=str(out),sha256=sha(out),derivedFrom=[checks["proposal"]],operation="Exact native crop",sourceRect=box))
for n in ["v2-proposal-frame.png","v2-proposal-candidate.png"]:
 out=D/n;write(D/(n+".generation.json"),dict(file=str(out),sha256=sha(out),derivedFrom=[m["candidate"],checks["generatedArtSource"]],mapping=str(D/"mapping.json"),checks=checks,actualModel=None,actualQuality=None))
write(D/"v2-proposal-checks.json",checks);print(json.dumps(checks))


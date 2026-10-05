from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,datetime,sys
R=Path(__file__).resolve().parent
C=R.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
idx=int(sys.argv[1]);host=Path(sys.argv[2]);P=R/f"patch-{idx:02d}"
rec=json.loads((P/"context.png.generation.json").read_text())
src=Path(rec["derivedFrom"]);assert sha(src)==rec["sourceSha256"]
shutil.copy2(host,P/"native.png")
a=np.array(Image.open(src).convert("RGB"));n=np.array(Image.open(P/"native.png").convert("RGB"))
assert n.shape==(1254,1254,3)
x0,y0,x1,y1=rec["cropLTRB"];y,x=np.mgrid[:1254,:1254]
edge=np.minimum(y,1253-y)
if x0>0:edge=np.minimum(edge,x)
if x1<a.shape[1]:edge=np.minimum(edge,1253-x)
t=np.clip((edge-16)/112,0,1);alpha=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
ctx=a[y0:y1,x0:x1].copy()
joined=((ctx.astype(np.uint32)*(255-alpha[:,:,None])+n.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
out=a.copy();out[y0:y1,x0:x1]=joined
dest=R/f"strip-{idx:02d}.png";Image.fromarray(out).save(dest)
Image.fromarray(joined).save(P/"composite.png");Image.fromarray(alpha).save(P/"mask.png")
bb=[max(0,x0-160),0,min(a.shape[1],x1+160),1254]
Image.fromarray(out).crop(bb).save(P/"perimeter.png")
receipt=R/f"tool-response-{idx:02d}.json"
d=np.any(out!=a,axis=2);ys,xs=np.where(d)
g={"file":str(P/"native.png"),"sha256":sha(P/"native.png"),"recordedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"actualModel":None,"actualQuality":None,"generatedAt":None,"width":1254,"height":1254,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads((C/"config.snapshot.json").read_text()),"submittedParameters":{"model":None,"quality":None,"size":None,"transparent_background":False},"unverifiedReason":"Host-managed builtin exposes no model/quality selectors or generation timestamp.","prompt":str(P/"prompt.txt"),"references":[rec,{"file":"D:/work/image/designs/gameplay-ui/04-guild.png","role":"approved style","sha256":sha("D:/work/image/designs/gameplay-ui/04-guild.png")}],"evidence":{"toolResponse":str(receipt),"hostSavedOriginal":str(host),"hostSha256":sha(host),"copyByteIdentical":sha(host)==sha(P/"native.png")}}
(P/"native.png.generation.json").write_text(json.dumps(g,indent=2),encoding="utf-8")
assembly={"candidate":{"file":str(dest),"sha256":sha(dest),"pixels":[4096,1254]},"derivedFrom":[{"file":str(src),"sha256":sha(src)},{"file":str(P/"native.png"),"sha256":sha(P/"native.png")}],"operation":"Native pixel composite. Smoothstep context mask 16..128px; global side edges have no x fade. No resize, geometric warp or source-image blur.","cropLTRB":rec["cropLTRB"],"changedPixels":int(d.sum()),"changedBoundsLTRB":[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],"outsideCropUnchanged":True}
(R/f"strip-{idx:02d}.json").write_text(json.dumps(assembly,indent=2),encoding="utf-8")
if idx<4:
 j=idx+1;x0=[0,948,1896,2842][idx];box=[x0,0,x0+1254,1254];Q=R/f"patch-{j:02d}";Q.mkdir(exist_ok=True)
 Image.fromarray(out).crop(box).save(Q/"context.png")
 rr={"file":str(Q/"context.png"),"sha256":sha(Q/"context.png"),"derivedFrom":str(dest),"sourceSha256":sha(dest),"cropLTRB":box,"operation":"native crop paired strip"}
 (Q/"context.png.generation.json").write_text(json.dumps(rr,indent=2),encoding="utf-8")
 shutil.copy2(P/"prompt.txt",Q/"prompt.txt")
print(json.dumps(assembly))

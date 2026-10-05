"""Native image repair ingest and deterministic alpha join, no creative raster painting."""
from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, shutil, sys, datetime
ROOT=Path(__file__).resolve().parent
patchdir=ROOT/sys.argv[1]
host=Path(sys.argv[2])
outdir=ROOT/sys.argv[3]
outdir.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
context_record=json.loads((patchdir/"context.png.generation.json").read_text())
base=Path(context_record["derivedFrom"])
native=patchdir/"native.png"
shutil.copy2(host,native)
a=np.array(Image.open(base).convert("RGB"))
n=np.array(Image.open(native).convert("RGB"));assert n.shape==(1254,1254,3)
x0,y0,x1,y1=context_record["cropLTRB"]
ctx=a[y0:y1,x0:x1].copy()
assert sha(base)==context_record["sourceSha256"]
y,x=np.mgrid[:1254,:1254];edge=np.minimum.reduce([x,y,1253-x,1253-y])
t=np.clip((edge-16)/112,0,1);mask=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
result=((ctx.astype(np.uint32)*(255-mask[:,:,None])+n.astype(np.uint32)*mask[:,:,None]+127)//255).astype(np.uint8)
out=a.copy();out[y0:y1,x0:x1]=result
Image.fromarray(out).save(outdir/"r08_c08.png")
Image.fromarray(result).save(patchdir/"composite.png")
Image.fromarray(mask).save(patchdir/"mask.png")
pbox=[max(0,x0-160),max(0,y0-160),min(4096,x1+160),min(4096,y1+160)]
Image.fromarray(out).crop(pbox).save(patchdir/"perimeter.png")
d=np.any(out!=a,axis=2);ys,xs=np.where(d)
generation={"file":str(native),"sha256":sha(native),"generatedAt":None,"recordedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"width":1254,"height":1254,"format":"PNG","tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads((ROOT/"config.snapshot.json").read_text()),"submittedParameters":{"model":None,"quality":None,"size":None,"transparent_background":False},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host managed; model, quality and server generation time were not disclosed.","prompt":str(patchdir/"prompt.txt"),"references":[context_record,{"file":"D:/work/image/designs/gameplay-ui/04-guild.png","role":"approved style reference","sha256":sha("D:/work/image/designs/gameplay-ui/04-guild.png")}],"evidence":{"toolResponse":str(patchdir/"tool-response.json"),"hostSavedOriginal":str(host),"hostSha256":sha(host),"copyByteIdentical":sha(native)==sha(host)}}
(patchdir/"native.png.generation.json").write_text(json.dumps(generation,indent=2),encoding="utf-8")
rec={"candidate":{"file":str(outdir/"r08_c08.png"),"sha256":sha(outdir/"r08_c08.png"),"pixels":[4096,4096]},"derivedFrom":[{"file":str(base),"sha256":sha(base)},{"file":str(native),"sha256":sha(native),"generation":str(patchdir/"native.png.generation.json")}],"operation":"Native 1254 crop composite, no upscale, geometric warp, blur or sharpening. Smoothstep edge 16..128 pixels; geometry repaired by actual AI image.","cropLTRB":[x0,y0,x1,y1],"mask":{"file":str(patchdir/"mask.png"),"sha256":sha(patchdir/"mask.png")},"changedPixels":int(d.sum()),"changedBoundsLTRB":[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],"pixelsOutsideCropUnchanged":True,"formalAccepted":False}
(outdir/"assembly.json").write_text(json.dumps(rec,indent=2),encoding="utf-8")
for name,box in [("composite.png",[x0,y0,x1,y1]),("perimeter.png",pbox)]:
 (patchdir/(name+".generation.json")).write_text(json.dumps({"file":str(patchdir/name),"sha256":sha(patchdir/name),"derivedFrom":rec["candidate"],"cropLTRB":box,"operation":"exact native crop"},indent=2))
print(json.dumps(rec["candidate"]))


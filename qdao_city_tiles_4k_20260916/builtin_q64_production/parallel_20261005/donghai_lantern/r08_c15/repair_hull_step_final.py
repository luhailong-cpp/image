from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent
ROOT=T.parent
D=T/"repairs/hull-step-final"
BASE=T/"repairs/approved-sync/output/r08_c15.png"
BASE_SHA="908df2ad815315cac373cf0ace48c0f2493e45b981b729ee28741cae5da82fa9"
W=[1960,2390,3214,3644]
ROIS=[[2460,2880,2680,3120]]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {"file":str(p),"sha256":sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding="utf-8"))
def write(p,j):
 p=Path(p);assert p.resolve().is_relative_to(D.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def save(p,im,meta):
 p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
 e={**ref(p),"pixels":list(im.size),"generatedByAI":False,"resized":False,**meta};write(str(p)+".generation.json",e);return e
def prepare():
 assert sha(BASE)==BASE_SHA
 assert not (D/"request.json").exists()
 for name in ("target","day-geometry"):
  rec=read(D/(name+".png.generation.json"));assert sha(rec["file"])==rec["sha256"];assert rec["tileRectXYXY"]==W
 refs=[{**ref(D/"target.png"),"role":"edit target current festival native same-window pixels"},{**ref(D/"day-geometry.png"),"role":"frozen approved DAY same-window geometry: continuous lower hull silhouette, never copy daylight colors"},{**ref(Path("D:/work/image/designs/gameplay-ui/04-guild.png")),"role":"confirmed clean rounded rich hand-painted Daoist Q style, ignore UI"}]
 prompt="""Use case: precise-object-edit. Image 1 is the exact EDIT TARGET, a 1254x1254 native Lantern Festival game map crop. Repair ONLY the tiny accidental inward notch/step in the lower edge of the boat hull near target pixel (605,628), within x500..720,y490..730. A short brown-to-blue splice at x590..640,y560..660 currently interrupts the long smooth diagonal boat/water contact line. Image 2 is the exact same-coordinate approved DAY geometry reference: its lower hull and thin blue water-contact rim are smooth and continuous at this location. Restore that same continuous local silhouette and wood-grain brushwork across the tiny splice. Follow the existing diagonal tangent and preserve the overall boat footprint, perspective, scale, plank seams, shadows and all objects. This is one tiny continuity correction, not a new shape or a redesign. Preserve the target's royal-blue water and warm peach-gold lantern reflections, rich warm-brown painted wood and existing lighting. Image 3 is only the confirmed clean rounded hand-painted Daoist Q style. Do not copy daylight colors or UI. Do not change composition, border pixels, add anything, erase reflection bands, blur, sharpen, warp, zoom, resize, add noise, text or glitter. Only the small local notch and its abrupt color transition should be repaired. Return one opaque native 1254 by 1254 image with exactly the same field of view and unchanged surrounding content."""
 (D/"prompt.txt").write_text(prompt,encoding="utf-8")
 write(D/"references.json",refs)
 request={"prompt":prompt,"referenced_image_paths":[x["file"] for x in refs],"transparent_background":False}
 write(D/"request.json",request)
 write(D/"prepared.json",{"base":ref(BASE),"windowXYXY":W,"roisXYXY":ROIS,"references":refs,"prompt":ref(D/"prompt.txt"),"dayGeometryActualView":"Same coordinate frozen DAY 70ce623a has smooth contact line; notch exists only in festival assembled 908df2ad.","daySyncRequired":False,"geometryChangeAllowed":"Only restore this tiny accidental notch to approved DAY continuous lower hull tangent; overall footprint unchanged."})
 print(json.dumps(request))
def record(raw):
 raw=Path(raw);n=D/"native.png";assert not n.exists()
 im=Image.open(raw);im.load();assert im.size==(1254,1254) and im.format=="PNG"
 for r in read(D/"references.json"):assert sha(r["file"])==r["sha256"]
 assert sha(BASE)==BASE_SHA
 shutil.copyfile(raw,n)
 write(str(n)+".generation.json",{**ref(n),"pixels":[1254,1254],"generatedAtUtc":datetime.now(timezone.utc).isoformat(),"route":"builtin","tool":"image_gen.imagegen","configSnapshot":read(ROOT/"batch-model-check.json")["configSnapshot"],"submittedParameters":{"model":None,"quality":None,**read(D/"request.json")},"actualModel":None,"actualQuality":None,"unverifiedReason":"Host-managed builtin exposes no actual model/quality metadata or selectors.","evidence":{"toolResultSourcePath":str(raw),"toolResultSha256":sha(raw)},"prompt":ref(D/"prompt.txt"),"request":ref(D/"request.json"),"references":read(D/"references.json"),"resizedAfterGeneration":False,"geometryChangeAllowed":"Restore only local unintended notch to frozen DAY continuous hull silhouette.","windowXYXY":W,"formalAccepted":False})
 print(json.dumps(ref(n)))
def patch():
 assert sha(BASE)==BASE_SHA
 old=np.asarray(Image.open(BASE).convert("RGB").crop(W));n=np.asarray(Image.open(D/"native.png").convert("RGB"))
 yy,xx=np.mgrid[:1254,:1254];a=np.zeros((1254,1254),np.uint8)
 for l,t,r,b in ROIS:
  d=np.minimum.reduce((xx+W[0]-l,yy+W[1]-t,r-1-xx-W[0],b-1-yy-W[1])).astype(np.float32)
  z=np.clip(d/48,0,1);np.maximum(a,np.rint(z*z*(3-2*z)*255).astype(np.uint8),out=a)
 m=save(D/"mask.png",Image.fromarray(a),{"windowXYXY":W,"roisXYXY":ROIS,"featherPixels":48,"operation":"zero-background 1254 mask with bounded local 48px inward smoothstep"})
 v=((old.astype(np.uint32)*(255-a[:,:,None])+n.astype(np.uint32)*a[:,:,None]+127)//255).astype(np.uint8)
 assert np.array_equal(v[a==0],old[a==0])
 out=save(D/"patched-window.png",Image.fromarray(v),{"base":ref(BASE),"native":ref(D/"native.png"),"mask":m,"windowXYXY":W,"outsideMaskPixelIdentical":True})
 full=Image.open(BASE).convert("RGB");full.paste(Image.fromarray(v),(W[0],W[1]))
 qa=[save(D/"qa/full1254.png",Image.fromarray(v),{"pixelScale":1})]
 for i,(l,t,r,b) in enumerate(ROIS):
  for side,box in {"left":[l-96,t-96,l+96,b+96],"right":[r-96,t-96,r+96,b+96],"top":[l-96,t-96,r+96,t+96],"bottom":[l-96,b-96,r+96,b+96]}.items():
   qa.append(save(D/f"qa/roi{i+1}-{side}.png",full.crop(box),{"cropXYXY":box,"pixelScale":1}))
 write(D/"completion.json",{"base":ref(BASE),"native":ref(D/"native.png"),"nativeRecord":ref(D/"native.png.generation.json"),"mask":m,"patchedWindow":out,"windowXYXY":W,"roisXYXY":ROIS,"outsideMaskPixelIdentical":True,"changedPixels":int(np.any(v!=old,axis=2).sum()),"geometryChangeAllowed":"Restore only unintended notch to frozen DAY continuous hull tangent; overall footprint fixed.","daySyncRequired":False,"qa":qa,"visualReview":"pending","fullTileComposited":False,"formalAccepted":False})
 print(json.dumps(out))
if __name__=="__main__":
 action=sys.argv[1]
 {"prepare":prepare,"record":lambda:record(sys.argv[2]),"patch":patch}[action]()


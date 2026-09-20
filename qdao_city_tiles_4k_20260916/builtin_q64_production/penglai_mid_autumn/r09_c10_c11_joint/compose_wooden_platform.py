
"""Mechanical placement of native seam repair into joint extended context. No generation."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
 d=ROOT/"repairs/wooden_platform_join";out=ROOT/"output/v2";qa=ROOT/"qa/v2";out.mkdir(parents=True,exist_ok=True);qa.mkdir(parents=True,exist_ok=True)
 src=ROOT/"output/extended-context.png";native=d/"repair-native.png";record=d/"repair.record.json";box=(3699,3072,4953,4326);manifest=out/"assembly.json"
 if a.check:
  j=json.loads(manifest.read_text());assert j["scriptSha256"]==sha(__file__)
  for s in j["sources"]: assert sha(s["path"])==s["sha256"]
  for o in j["outputs"]:assert sha(ROOT/o["file"])==o["sha256"]
  old=np.array(Image.open(src));new=np.array(Image.open(out/"extended-context.png"));pair=np.array(Image.open(out/"pair-8192x4096.png"))
  outside=np.ones(old.shape[:2],bool);outside[box[1]:box[3],box[0]:box[2]]=False
  assert np.array_equal(old[outside],new[outside]);assert np.array_equal(new[115:4211,115:8307],pair)
  for c in range(2): assert np.array_equal(pair[:,4096*c:4096*(c+1)],np.array(Image.open(out/f"penglai_mid_autumn_r09_c{10+c:02d}_4k_joint_candidate_v2.png")))
  print(json.dumps({"check":True,"pairPixels":[8192,4096],"outsideRepairUnchanged":True,"splitPixelIdentity":True}));return
 rec=json.loads(record.read_text());assert rec["route"]=="builtin_image_gen" and rec["backendModelVerified"] is False
 for p,key in [(native,"outputSha256"),(d/"before.png","guideSha256"),(d/"repair.prompt.txt","promptSha256"),(d/"input-preview.jpg","submittedImageSha256")]:assert sha(p)==rec[key]
 assert sha(rec["sourceOutputPath"])==sha(native);assert rec["actualNativePixels"]==[1254,1254]
 old=np.array(Image.open(src).convert("RGB"));art=np.array(Image.open(native).convert("RGB"));ctx=old[box[1]:box[3],box[0]:box[2]].copy()
 assert ctx.shape==art.shape==(1254,1254,3);assert np.array_equal(ctx,np.array(Image.open(d/"before.png")))
 asm=mod(ROOT.parent/"r09_c11/assemble_builtin.py","builtin_seams");seam=asm.load_seam_helper()
 h,w=ctx.shape[:2];band=96;mask=np.full((h,w),255,np.uint8)
 sl=seam(ctx[:,:band],art[:,:band]);mask[:,:band]=np.uint8(np.arange(band)[None,:]>=sl[:,None])*255
 sr=seam(ctx[:,-band:][:,::-1],art[:,-band:][:,::-1]);mask[:,-band:]=np.minimum(mask[:,-band:],(np.uint8(np.arange(band)[None,:]>=sr[:,None])*255)[:,::-1])
 st=seam(np.transpose(ctx[:band],(1,0,2)),np.transpose(art[:band],(1,0,2)));top=np.uint8(np.arange(band)[:,None]>=st[None,:])*255;mask[:band]=np.minimum(mask[:band],top)
 mask=np.array(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(2)))
 join=mod(PROJECT/"tools/mechanical_join.py","registered_helper")
 joined,flow,correction,report=join.registered_join(ctx,art,mask,edges=("left","right","top"),max_shift=4.0,flow_inner=160,flow_full=48,tone_inner=180,tone_full=72)
 new=old.copy();new[box[1]:box[3],box[0]:box[2]]=joined
 ext=Image.fromarray(new);pair=ext.crop((115,115,8307,4211));files=[]
 def save(im,p):
  im.save(p,format="PNG");files.append({"file":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"pixels":list(im.size)})
 save(ext,out/"extended-context.png");save(pair,out/"pair-8192x4096.png")
 for c in range(2):save(pair.crop((4096*c,0,4096*(c+1),4096)),out/f"penglai_mid_autumn_r09_c{10+c:02d}_4k_joint_candidate_v2.png")
 Image.fromarray(mask).save(out/"repair-mask.png");np.savez_compressed(out/"repair-boundary-registration.npz",flow=flow,correction=correction,mask=mask)
 pair.resize((1536,768),Image.Resampling.LANCZOS).save(qa/"overview.jpg",quality=90)
 for y in (0,1024,2048,3072):pair.crop((3796,y,4396,y+1024)).save(qa/f"shared_boundary_y{y:04d}_100pct.jpg",quality=95)
 Image.fromarray(joined).save(qa/"repair-composed_100pct.jpg",quality=95)
 for name,bb in {"repair_left_100pct":(3549,3072,3849,4326),"repair_right_100pct":(4803,3072,5103,4326),"repair_top_100pct":(3699,2922,4953,3222)}.items():
  crop=ext.crop(bb)
  if name=="repair_top_100pct":crop=crop.transpose(Image.Transpose.ROTATE_90)
  crop.save(qa/f"{name}.jpg",quality=95)
 rt=pair.crop((4096,0,8192,4096))
 for axis in ("x","y"):
  for pos in (1024,2048,3072):
   strip=rt.crop((pos-150,0,pos+150,4096)) if axis=="x" else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
   sheet=Image.new("RGB",(1200,1024))
   for k in range(4):sheet.paste(strip.crop((0,k*1024,300,(k+1)*1024)),(300*k,0))
   sheet.save(qa/f"right_internal_{axis}{pos}_100pct.jpg",quality=95)
 sources=[{"path":str(p),"sha256":sha(p)} for p in (src,ROOT/"output/assembly.json",native,record,d/"plan.json",d/"repair.prompt.txt",d/"before.png",PROJECT/"tools/mechanical_join.py")]
 j={"schemaVersion":1,"appearance":"penglai_mid_autumn","status":"candidate_pending_visual_QA_not_published","createdAtUtc":datetime.now(timezone.utc).isoformat(),"scriptPath":str(Path(__file__).resolve()),"scriptSha256":sha(__file__),"sources":sources,"repairExtendedBoxLTRB":box,"repairPairBoxLTRB":[3584,2957,4838,4211],"nativeRepairPixels":[1254,1254],"jointPixels":[8422,4326],"pairPixels":[8192,4096],"deliveryPixelsEach":[4096,4096],"cropLTRB":[115,115,8307,4211],"globalPairPixelRectXYWH":[36864,32768,8192,4096],"method":"Three-edge96px minimum-error seam plus2px integer mask blend; bounded subpixel registration and low-frequency edge tone matching; no bottom blend because source covers bottom external halo","registration":report,"finalArtUpscaled":False,"sourcePngUnchanged":True,"outsideRepairBoxUnchanged":True,"outputs":files,"qa":{"status":"pending","otherNeighborEdgesAccepted":False,"runtimeAccepted":False}}
 manifest.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"assembly":str(manifest),"repairRegistration":report}))
if __name__=="__main__":main()


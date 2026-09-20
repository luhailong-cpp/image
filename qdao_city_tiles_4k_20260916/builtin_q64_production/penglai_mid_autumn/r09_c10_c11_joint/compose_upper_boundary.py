
"""Mechanical native repair pair assembly into the upper shared boundary."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--check",action="store_true");a=ap.parse_args()
 d=ROOT/"repairs/upper_shared_boundary";out=ROOT/"output/v3";qa=ROOT/"qa/v3";out.mkdir(parents=True,exist_ok=True);qa.mkdir(parents=True,exist_ok=True)
 src=ROOT/"output/v2/extended-context.png";box=(3699,0,4953,2278);manifest=out/"assembly.json"
 if a.check:
  j=json.loads(manifest.read_text());assert j["scriptSha256"]==sha(__file__)
  for s in j["sources"]:assert sha(s["path"])==s["sha256"]
  for o in j["outputs"]:assert sha(ROOT/o["file"])==o["sha256"]
  old=np.array(Image.open(src));new=np.array(Image.open(out/"extended-context.png"));pair=np.array(Image.open(out/"pair-8192x4096.png"))
  outside=np.ones(old.shape[:2],bool);outside[box[1]:box[3],box[0]:box[2]]=False;assert np.array_equal(old[outside],new[outside]);assert np.array_equal(new[115:4211,115:8307],pair)
  for c in range(2):assert np.array_equal(pair[:,4096*c:4096*(c+1)],np.array(Image.open(out/f"penglai_mid_autumn_r09_c{10+c:02d}_4k_joint_candidate_v3.png")))
  print(json.dumps({"check":True,"pairPixels":[8192,4096],"outsideRepairUnchanged":True,"splitPixelIdentity":True}));return
 sourcepaths=[src,ROOT/"output/v2/assembly.json",d/"plan.json",BASE/"tools/mechanical_join.py"]
 natives=[]
 for tid in ("r01_c01","r02_c01"):
  rp=d/"native"/f"{tid}.record.json";r=json.loads(rp.read_text());assert r["backendModelVerified"] is False and r["route"]=="builtin_image_gen";assert r["actualNativePixels"]==[1254,1254]
  files=[(d/"native"/f"{tid}.png","outputSha256"),(d/"prompts"/f"{tid}.prompt.txt","promptSha256"),(d/"guides"/f"{tid}.png","guideSha256"),(d/"guides"/f"{tid}.jpg","submittedImageSha256")]
  for p,k in files:assert sha(p)==r[k];sourcepaths.append(p)
  assert sha(r["sourceOutputPath"])==r["outputSha256"];sourcepaths.append(rp)
  im=Image.open(files[0][0]);assert im.size==(1254,1254);assert im.mode=="RGB" or im.getextrema()[3]==(255,255);natives.append(np.array(im.convert("RGB")))
 asm=mod(ROOT.parent/"r09_c11/assemble_builtin.py","builtin_seams");seam=asm.load_seam_helper()
 joined,joinmetric=asm.append_patch(natives[0].transpose(1,0,2),natives[1].transpose(1,0,2),seam,"repair_internal_horizontal")
 art=joined.transpose(1,0,2);assert art.shape==(2278,1254,3)
 Image.fromarray(art).save(out/"joined-native-repair.png")
 old=np.array(Image.open(src).convert("RGB"));ctx=old[0:2278,3699:4953].copy();h,w=ctx.shape[:2];band=96;mask=np.full((h,w),255,np.uint8)
 sl=seam(ctx[:,:band],art[:,:band]);mask[:,:band]=np.uint8(np.arange(band)[None,:]>=sl[:,None])*255
 sr=seam(ctx[:,-band:][:,::-1],art[:,-band:][:,::-1]);mask[:,-band:]=np.minimum(mask[:,-band:],(np.uint8(np.arange(band)[None,:]>=sr[:,None])*255)[:,::-1])
 sb=seam(ctx[-band:][::-1].transpose(1,0,2),art[-band:][::-1].transpose(1,0,2));bot=(np.uint8(np.arange(band)[:,None]>=sb[None,:])*255)[::-1];mask[-band:]=np.minimum(mask[-band:],bot)
 mask=np.array(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(2)))
 join=mod(BASE/"tools/mechanical_join.py","registered_helper")
 result,flow,correction,report=join.registered_join(ctx,art,mask,edges=("left","right","bottom"),max_shift=4,flow_inner=160,flow_full=48,tone_inner=180,tone_full=72)
 new=old.copy();new[0:2278,3699:4953]=result;ext=Image.fromarray(new);pair=ext.crop((115,115,8307,4211));files=[]
 def save(im,p):
  im.save(p,format="PNG");files.append({"file":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":sha(p),"pixels":list(im.size)})
 save(ext,out/"extended-context.png");save(pair,out/"pair-8192x4096.png")
 for c in range(2):save(pair.crop((4096*c,0,4096*(c+1),4096)),out/f"penglai_mid_autumn_r09_c{10+c:02d}_4k_joint_candidate_v3.png")
 Image.fromarray(mask).save(out/"repair-mask.png");np.savez_compressed(out/"repair-boundary-registration.npz",flow=flow,correction=correction,mask=mask)
 pair.resize((1536,768),Image.Resampling.LANCZOS).save(qa/"overview.jpg",quality=90)
 for y in (0,1024,2048,3072):pair.crop((3796,y,4396,y+1024)).save(qa/f"shared_boundary_y{y:04d}_100pct.jpg",quality=95)
 for name,x in (("left",3699),("right",4953)):
  for y in (0,1024,1254):ext.crop((x-150,y,x+150,y+1024)).save(qa/f"repair_{name}_y{y}_100pct.jpg",quality=95)
 ext.crop((3699,2128,4953,2428)).transpose(Image.Transpose.ROTATE_90).save(qa/"repair_bottom_100pct.jpg",quality=95)
 ext.crop((3699,874,4953,1174)).transpose(Image.Transpose.ROTATE_90).save(qa/"repair_internal_join_100pct.jpg",quality=95)
 rt=pair.crop((4096,0,8192,4096))
 for axis in ("x","y"):
  for pos in (1024,2048,3072):
   strip=rt.crop((pos-150,0,pos+150,4096)) if axis=="x" else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
   sheet=Image.new("RGB",(1200,1024))
   for k in range(4):sheet.paste(strip.crop((0,k*1024,300,(k+1)*1024)),(300*k,0))
   sheet.save(qa/f"right_internal_{axis}{pos}_100pct.jpg",quality=95)
 rec={"schemaVersion":1,"appearance":"penglai_mid_autumn","status":"candidate_pending_visual_QA_not_published","createdAtUtc":datetime.now(timezone.utc).isoformat(),"scriptPath":str(Path(__file__).resolve()),"scriptSha256":sha(__file__),"sources":[{"path":str(p),"sha256":sha(p)} for p in sourcepaths],"repairExtendedBoxLTRB":box,"repairPairBoxLTRB":[3584,-115,4838,2163],"nativeRepairSources":2,"nativePixelsEach":[1254,1254],"joinedNativePixels":[1254,2278],"nativeJoin":joinmetric,"jointPixels":[8422,4326],"pairPixels":[8192,4096],"deliveryPixelsEach":[4096,4096],"cropLTRB":[115,115,8307,4211],"globalPairPixelRectXYWH":[36864,32768,8192,4096],"method":"Native pair230px minimum seam, then3-edge96px seam with2px integer mask blend, bounded subpixel edge registration and local tone matching; no top blend because patch includes top external halo","registration":report,"finalArtUpscaled":False,"sourcePngUnchanged":True,"outsideRepairBoxUnchanged":True,"outputs":files,"qa":{"status":"pending","otherNeighborEdgesAccepted":False,"runtimeAccepted":False}}
 manifest.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps({"assembly":str(manifest),"registration":report}))
if __name__=="__main__":main()


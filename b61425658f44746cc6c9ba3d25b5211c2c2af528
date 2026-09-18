"""Joint assembly of two neighboring native-derived 4K tiles. No image generation."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadmod(p):
 s=importlib.util.spec_from_file_location("patch_assembler",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument("appearance",choices=["penglai_day","penglai_mid_autumn"]);ap.add_argument("--check",action="store_true");a=ap.parse_args()
 city=BASE/a.appearance;root=city/"r09_c10_c11_joint";out=root/"output";qa=root/"qa";out.mkdir(parents=True,exist_ok=True);qa.mkdir(exist_ok=True)
 oldver="v2_registered" if a.appearance=="penglai_day" else "v3_registered"
 left=city/"r09_c10"/"output"/oldver/"extended-context.png";right=city/"r09_c11"/"output"/"extended-context.png";manifest=out/"assembly.json"
 if a.check:
  r=json.loads(manifest.read_text());assert r["scriptSha256"]==sha(__file__)
  for s in r["sources"]:
   assert sha(s["contextPath"])==s["contextSha256"];assert sha(s["assemblyPath"])==s["assemblySha256"]
  for s in r["outputs"]: assert sha(root/s["file"])==s["sha256"]
  ext=np.array(Image.open(out/"extended-context.png"));pair=np.array(Image.open(out/"pair-8192x4096.png"))
  assert ext.shape==(4326,8422,3) and pair.shape==(4096,8192,3)
  assert np.array_equal(ext[115:4211,115:8307],pair)
  for c in range(2):assert np.array_equal(pair[:,4096*c:4096*(c+1)],np.array(Image.open(out/f"{a.appearance}_r09_c{10+c:02d}_4k_joint_candidate.png")))
  print(json.dumps({"check":True,"appearance":a.appearance,"pairPixels":[8192,4096],"splitPixelIdentity":True}));return
 m=loadmod(city/"r09_c11"/"assemble_builtin.py");seam=m.load_seam_helper()
 l=np.array(Image.open(left).convert("RGB"));r=np.array(Image.open(right).convert("RGB"));assert l.shape==r.shape==(4326,4326,3)
 extended,metric=m.append_patch(l,r,seam,"cross_tile_r09_c10_to_c11")
 assert extended.shape==(4326,8422,3);assert np.array_equal(extended[:,:4096],l[:,:4096]);assert np.array_equal(extended[:,4326:],r[:,230:])
 pair=Image.fromarray(extended).crop((115,115,8307,4211))
 files=[]
 def save(im,p):
  im.save(p,format="PNG");files.append({"file":str(p.relative_to(root)).replace("\\","/"),"size":list(im.size),"sha256":sha(p)})
 save(Image.fromarray(extended),out/"extended-context.png");save(pair,out/"pair-8192x4096.png")
 for c in range(2):save(pair.crop((4096*c,0,4096*(c+1),4096)),out/f"{a.appearance}_r09_c{10+c:02d}_4k_joint_candidate.png")
 pair.resize((1536,768),Image.Resampling.LANCZOS).save(qa/"overview.jpg",quality=90)
 for row in range(4):
  pair.crop((3796,1024*row,4396,1024*(row+1))).save(qa/f"shared_boundary_y{row*1024:04d}_100pct.jpg",quality=95)
 # Every internal line in right tile, unscaled 300px-wide strips split into four sections.
 rt=pair.crop((4096,0,8192,4096))
 for axis in ("x","y"):
  for pos in (1024,2048,3072):
   strip=rt.crop((pos-150,0,pos+150,4096)) if axis=="x" else rt.crop((0,pos-150,4096,pos+150)).transpose(Image.Transpose.ROTATE_90)
   sheet=Image.new("RGB",(1200,1024))
   for k in range(4):sheet.paste(strip.crop((0,k*1024,300,(k+1)*1024)),(300*k,0))
   sheet.save(qa/f"right_internal_{axis}{pos}_100pct.jpg",quality=95)
 inputs=[]
 for p in(left,right):
  assembly=p.parent/"assembly.json";assert assembly.exists()
  inputs.append({"contextPath":str(p),"contextSha256":sha(p),"assemblyPath":str(assembly),"assemblySha256":sha(assembly)})
 rec={"schemaVersion":1,"appearance":a.appearance,"status":"candidate_pending_visual_QA_not_published","createdAtUtc":datetime.now(timezone.utc).isoformat(),"scriptPath":str(Path(__file__).resolve()),"scriptSha256":sha(__file__),"sources":inputs,"geometry":{"sourcePixelsEach":[4326,4326],"overlap":230,"joinedPixels":[8422,4326],"cropLTRB":[115,115,8307,4211],"pairPixels":[8192,4096],"splitAtX":4096,"globalPairPixelRectXYWH":[36864,32768,8192,4096]},"method":"230px minimum-error seam with 2px integer blend, then one outer crop and exact split","jointStageResampling":False,"jointStageColorMatching":False,"finalArtUpscaled":False,"upstreamProcessing":"Left input contains explicitly recorded local boundary registration and tone matching; see source assembly. Right input native patches joined without resampling.","unchangedOutsideSharedOverlap":True,"seam":metric,"outputs":files,"qa":{"overview":"qa/overview.jpg","sharedBoundary":"qa/shared_boundary_y*_100pct.jpg","rightInternalLines":"qa/right_internal_*_100pct.jpg","visualStatus":"pending","externalOtherEdges":"not_verified_with_neighbor_tiles","runtimeAcceptance":False}}
 manifest.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({"appearance":a.appearance,"assembly":str(manifest),"pair":str(out/"pair-8192x4096.png")}))
if __name__=="__main__":main()


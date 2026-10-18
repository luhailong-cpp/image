"""Batch-local wall geometry reference/QA helper. No generation, selection, shared writes."""
from pathlib import Path
from PIL import Image
import json, hashlib, datetime, argparse
B=Path(__file__).resolve().parent
R=B.parent.parent.parent.parent
def rd(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,o):
 with Path(p).open("x",encoding="utf-8") as f: json.dump(o,f,ensure_ascii=False,indent=2)
def png(p,im):
 with Path(p).open("xb") as f: im.save(f,format="PNG")
def free(stem,parent,suffix):
 for n in range(1,1000):
  p=parent/f"{stem}-v{n:03d}{suffix}"
  if not p.exists(): return p
 raise RuntimeError("Version range exhausted")
def native(p):
 p=Path(p);r=rd(p.with_suffix(".png.generation.json"));assert sha(p)==r["sha256"] and r["pixels"]==[1254,1254]
 return r
def intersect(a,b):
 x0,y0=max(a[0],b[0]),max(a[1],b[1]);x1,y1=min(a[2],b[2]),min(a[3],b[3])
 return [x0,y0,x1,y1] if x1>x0 and y1>y0 else None
def make(prepared,north,side):
 req=rd(prepared);p=req["coordinates"];assert req["tile"]=="r01_c04" and p["subrow"] in (2,3)
 world=p["worldBoxWithHalo"];contract=rd(B.parent.parent/"main-city-game-20261009/production-contract.json");layout=Path(contract["layoutReference"])
 assert sha(layout)==contract["layoutSha256"]
 with Image.open(layout) as raw:
  w,h=raw.size;extent=[world[0]*w/65536,world[1]*h/65536,world[2]*w/65536,world[3]*h/65536]
  guide=raw.convert("RGB").transform((1254,1254),Image.Transform.EXTENT,extent,Image.Resampling.BICUBIC)
 pastes=[]
 # Side continuation first; selected valid north core last at crossing.
 for role,f in [("locally_corrected_side_continuation",side),("north_valid_continuation",north)]:
  if not f or f=="-":continue
  ref=native(f);wb=ref["coordinates"]["worldBoxWithHalo"];allowed=list(wb)
  if p["subrow"]==2 and role=="north_valid_continuation":allowed[3]=1024
  overlap=intersect(world,allowed);assert overlap
  crop=[overlap[0]-wb[0],overlap[1]-wb[1],overlap[2]-wb[0],overlap[3]-wb[1]];dest=[overlap[0]-world[0],overlap[1]-world[1]]
  with Image.open(f) as raw:guide.paste(raw.convert("RGB").crop(crop),tuple(dest))
  pastes.append({"file":str(f),"sha256":sha(f),"role":role,"sourceWorldBox":wb,"allowedWorldBox":allowed,"sourceCropLTRB":crop,"guidePasteXY":dest,"resampled":False,"selectedStatusNotInferred":True,"authorization":"Root accepted corrected sample/authorized local continuation after actual layout+stable-edge review; no selection conferred."})
 directory=B/"requests/r01_c04";out=free(req["patch"]+"-wall-top-geometry",directory,".json");gp=out.with_suffix(".guide.png");png(gp,guide)
 if p["subrow"]==2:
  task="""Correct architecture: continue a BROAD LIGHT STONE HORIZONTAL WALL-TOP WALKWAY seen from above, between the rear parapet at top and the near/front coping below. Continue the rear parapet down to abouty200, the broad sunlit ivory/light-gray horizontal top plane across y200..810, and the straight front coping aroundy810..958. These heights continue exactly from the accepted sharp side native strip. Maintain the existing SHORT upright stone post wherever its faint approved-layout silhouette occurs; do not duplicate the side-reference post or import a new one. Its cap and stem belong to the near coping. Continue the front face and cast shadow below the coping to the crop bottom. Do not replace this depth with stacked vertical brick courses or collapse the horizontal plane to a thin stripe. Newly paint fine clean slab detail, subtle foliage shadow and pale stone finish, no noisy tiled texture."""
 else:
  task="""Continue only the TOP wall geometry correction: the correctly repaired near coping/front face and its shadow enter from the sharp north native strip. Carry that architecture smoothly through the upper portion, down to approximately worldY2450 (local y517), preserving its height, pale stone, overhang and front-wall layering. Below that, follow the approved original layout's actual existing wall and plaque shapes without enlarging, ornamenting or redesigning them. The plaque remains outside this top-geometry acceptance and will need separate review. Do not propagate the withdrawn all-height continuous-brick wall into the corrected upper band."""
 req.update(schemaVersion=8,createdAtUTC=now(),prompt=f"""Use case: precise-object-edit.
Asset: native1254x1254 opaque daylight city-map crop r01_c04/{req["patch"]}, world {world}; central1024 core [115,115,1139,1139]. Keep zoom, camera, frame and world alignment.
Image1 is a registered spatial edit target: enlarged low-resolution approved layout ONLY where blurry, combined with same-world sharp native corrected neighbor strips. Newly paint the blurry areas, never enlarge or sharpen them as final detail. Sharp strips are geometric endpoints at their exact coordinates; continue them naturally without straight pasted cutoffs. The northern first-row source is restricted to its real core pixels only (top115 here), no old erroneous southern halo is fixed.
{task}
Image2 is the enlarged approved whole-tile layout ONLY for layer order and approximate silhouettes, never native details. Image3 is the actual whole-city approved layout only. Images4/5 are the confirmed Daoist chibi painted originals for materials only: no UI, lettering, characters or night scene. Keep consistent stone hue, rounded hand-painted shading, fine crisp contours and daylight. No red plaque/new decoration unless actually shown in the local approved guide; no roofs, plants, poles or furnishings added. No photographic grit, honeycomb tessellation, plastic sheen, blur, feathering, border or labels. Output one native1254x1254 opaque painted continuation.""",
 referenced_image_paths=[str(gp),str(B/"r01_c04/qa/draft-native4096-v001/approved-layout-enlarged-context.png"),str(layout),str(R/"designs/mail-ui-v1/01-mail-event.png"),str(R/"designs/team-ui-v2/team-ui-v2.png")],
 guide={"file":str(gp),"sha256":sha(gp),"productionNativeSource":False,"layout":str(layout),"layoutSHA256":sha(layout),"sourceLayoutExtentLTRB":extent,"isEnlargedLayoutGuideOnly":True,"nativeContextPastes":pastes,"excludedOldWrongBrickGeometry":True},
 derivedFromPreparedRequest={"file":str(prepared),"sha256":sha(prepared)},geometryRepair={"rootAuthorization":"Continue after accepted s02_02-v002 pilot, no repeated confirmation; no selection writes.","scopeOnly":"r01_c04/s02_01..04 plus s03_01..04 top geometry","approxWholeRepairWorldBox":[12288,1250,16384,2450],"approxContourToleranceAcknowledged":"100worldpx is about2 original layout pixels; maintain accepted front coping and posts."},
 ruleSnapshot=[{"file":str(f),"sha256":sha(f)} for f in [R/"AGENTS.md",R/"docs/MAP_PARALLEL_SPLIT_20261013.json"]])
 wr(out,req);return {"request":str(out),"guide":str(gp),"nativeContextPastes":pastes}
def qa(file,north,side):
 rec=native(file);p=rec["patch"];parent=B/"r01_c04/qa";q=free(p+"-wall-top",parent,"");q.mkdir()
 im=Image.open(file).convert("RGB");items=[]
 if north and north!="-":
  ni=Image.open(north).convert("RGB");out=Image.new("RGB",(1024,320));out.paste(ni.crop((115,979,1139,1139)),(0,0));out.paste(im.crop((115,115,1139,275)),(0,160));items.append(("north-hard-core-native100.png",out,{"neighbor":str(north),"neighborSHA256":sha(north),"seamY":160}))
 if side and side!="-":
  ref=native(side);si=Image.open(side).convert("RGB");out=Image.new("RGB",(320,1024))
  west=ref["coordinates"]["worldBoxWithHalo"][0]<rec["coordinates"]["worldBoxWithHalo"][0]
  a,b=(si,im) if west else (im,si)
  out.paste(a.crop((979,115,1139,1139)),(0,0));out.paste(b.crop((115,115,275,1139)),(160,0));items.append((("west" if west else "east")+"-hard-core-native100.png",out,{"neighbor":str(side),"neighborSHA256":sha(side),"seamX":160}))
 items.append(("central-geometry-native100.png",im.crop((115,115,1139,1139)),{"cropLTRB":[115,115,1139,1139]}))
 crops=[]
 for name,out,extra in items:
  f=q/name;png(f,out);crops.append({"file":str(f),"sha256":sha(f),"pixels":list(out.size),"nativePixelScale":1,"resampled":False,**extra})
 m=q/"evidence-manifest-v001.json";wr(m,{"createdAtUTC":now(),"file":str(file),"sha256":sha(file),"patch":p,"scope":"wall top geometry only","formalAccepted":False,"selectionWritten":False,"crops":crops})
 return {"qaDirectory":str(q),"manifest":str(m),"crops":[x["file"] for x in crops]}
if __name__=="__main__":
 import sys
 if sys.argv[1]=="make":result=make(*sys.argv[2:])
 elif sys.argv[1]=="qa":result=qa(*sys.argv[2:])
 else:raise RuntimeError("unknown action")
 print(json.dumps(result,ensure_ascii=False))

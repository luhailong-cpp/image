from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"provenance"/"hit"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[];errors=[]
for d in ("E","W"):
 for i in range(1,7):
  p=ROOT/"frames"/"hit"/d/("frame_%02d.png"%i)
  if not p.exists():errors.append("missing "+str(p));continue
  with Image.open(p) as im:
   im.load();dims=list(im.size);mode=im.mode;alpha=list(im.getchannel("A").getextrema())
  r=json.loads(p.with_suffix(".generation.json").read_text(encoding="utf-8-sig"))
  if dims!=[1024,1024] or mode!="RGBA" or alpha!=[0,255]:errors.append("pixel contract "+str(p))
  if r["sha256"]!=sha(p):errors.append("sha mismatch "+str(p))
  n=ROOT/r["nativeSource"]["path"]
  if n.exists() and sha(n)!=r["nativeSource"]["sha256"]:errors.append("native sha "+str(n))
  if min(r["nativeSource"]["width"],r["nativeSource"]["height"])<1024:errors.append("small native "+str(p))
  if r["actualModel"] is not None or r["actualQuality"] is not None:errors.append("unsupported model claim "+str(p))
  for ref in r["references"]:
   if ref.get("fileRetained") is False:continue
   q=Path(ref["path"])
   if not q.exists() or sha(q)!=ref["sha256"]:errors.append("reference mismatch "+str(q))
  records.append({"file":p.relative_to(ROOT).as_posix(),"sha256":sha(p),"dimensions":dims,"mode":mode,"nativeDimensions":[r["nativeSource"]["width"],r["nativeSource"]["height"]],"frameDurationMs":r["frameDurationMs"]})
if len({r["sha256"] for r in records})!=len(records):errors.append("duplicate frame pixels")
gifs=[]
for d in ("E","W"):
 for name,ms in (("normal",40),("slow",160)):
  p=OUT/("hit_"+d+"_"+name+".gif")
  if not p.exists():continue
  with Image.open(p) as im:
   durations=[]
   for i in range(im.n_frames):im.seek(i);durations.append(im.info.get("duration"))
  if durations!=[ms]*6:errors.append("GIF timing "+str(p))
  gifs.append({"file":p.relative_to(ROOT).as_posix(),"frames":len(durations),"durationsMs":durations,"totalMs":sum(durations)})
result={"checkedAt":datetime.now(timezone.utc).isoformat(),"technicalStatus":"passed" if not errors else "failed","frameCount":len(records),"uniqueFrameCount":len({r["sha256"] for r in records}),"frames":records,"previews":gifs,"errors":errors,"limits":["技术契约不等同于动态美术通过。","帧组静态逐帧检查另见HIT_NOTES；根锚点仅布局目标，不冒称像素验证。","子代理Cua无可用浏览器，现场正常/慢速播放交父线程复核。"],"clientIntegration":"not_integrated"}
(OUT/"hit_technical_validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"status":result["technicalStatus"],"frames":len(records),"unique":result["uniqueFrameCount"],"gifPreviews":len(gifs),"errors":errors},ensure_ascii=False))


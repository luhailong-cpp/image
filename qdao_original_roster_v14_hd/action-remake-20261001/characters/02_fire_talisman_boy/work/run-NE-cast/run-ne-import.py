import argparse, hashlib, json, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument("--record",required=True)
ap.add_argument("--direction",choices=["NE"],required=True)
ap.add_argument("--frame",type=int,required=True)
ap.add_argument("--candidate")
ap.add_argument("--replace",action="store_true")
a=ap.parse_args()
if a.frame not in (7,8,10,11,12,13,14,15,16): raise RuntimeError("NE delegated slot boundary")
record_path=ROOT/a.record
record=json.loads(record_path.read_text(encoding="utf-8-sig"))
src=ROOT/record["file"]
with Image.open(src) as im:
    im.load()
    native=im.size
    if min(native)<1024: raise RuntimeError("native frame too small")
    if im.mode!="RGBA": raise RuntimeError("native source is not RGBA")
    alpha_hist=im.getchannel("A").histogram()
    record.update({"sha256":sha(src),"width":native[0],"height":native[1],"format":"PNG","mode":"RGBA"})
    record["technicalQA"]={"nativeSingleFrame":True,"transparentPixels":alpha_hist[0],"partialAlphaPixels":sum(alpha_hist[1:255]),"alphaBounds":im.getchannel("A").getbbox()}
    out=im.resize((1024,1024),Image.Resampling.LANCZOS)
dst=ROOT/"frames"/"run"/a.direction/f"{a.frame:02d}.png"
if a.candidate:
    dst=(ROOT/a.candidate).resolve()
    if not dst.is_relative_to(ROOT/"work"/"run-NE-cast"): raise RuntimeError("candidate path outside cast workspace")
dst.parent.mkdir(parents=True,exist_ok=True)
if dst.exists() and not a.replace: raise RuntimeError("refuse overwrite existing frame without explicit replacement")
out.save(dst)
output_sha=sha(dst)
record["export"]={"file":dst.relative_to(ROOT).as_posix(),"sha256":output_sha,"width":1024,"height":1024,"format":"PNG","mode":"RGBA","operation":"统一整画布由原生尺寸缩小为1024x1024，Pillow LANCZOS；无裁边、镜像、bbox缩放或逐帧贴地","derivedFrom":{"file":src.relative_to(ROOT).as_posix(),"sha256":sha(src),"native_size":list(native)}}
record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if a.candidate:
    print(json.dumps({"export":record["export"],"technicalQA":record["technicalQA"]},ensure_ascii=False))
    raise SystemExit(0)
ip=ROOT/"inventory-run-ne-cast.json"
inventory=json.loads(ip.read_text(encoding="utf-8-sig")) if ip.exists() else {"character":"02_fire_talisman_boy","root_anchor":[512,920],"action":"run","target_frames":9,"frame_duration_ms":75,"duration_ms":1200,"timing_status":"用户最新要求：16帧均匀75ms，总1200ms；客户端未确认","frames":[]}
entry={"action":"run","direction":a.direction,"frame":a.frame,"path":dst.relative_to(ROOT).as_posix(),"native_size":list(native),"native_evidence":a.record,"source_record":a.record,"sha256":output_sha,"visual_status":record.get("visualQA",{}).get("status","not_reviewed"),"client_status":"not_integrated"}
inventory["frames"]=[f for f in inventory["frames"] if (f["direction"],f["frame"])!=(a.direction,a.frame)]+[entry]
inventory["frames"].sort(key=lambda f:(f["direction"],f["frame"]))
ip.write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"export":entry,"count":len(inventory["frames"])},ensure_ascii=False))




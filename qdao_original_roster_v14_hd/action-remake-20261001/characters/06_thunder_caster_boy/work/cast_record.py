import argparse, hashlib, json, re, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(p):
 p=p.resolve()
 if not p.is_relative_to(ROOT.resolve()): raise ValueError("outside character")
 return p
ap=argparse.ArgumentParser()
ap.add_argument("source"); ap.add_argument("stem"); ap.add_argument("prompt"); ap.add_argument("direction"); ap.add_argument("frame",type=int)
ap.add_argument("--extra",action="append",default=[]); ap.add_argument("--started"); ap.add_argument("--export",action="store_true"); ap.add_argument("--review",default="static_pass_provisional")
a=ap.parse_args()
dest=safe(ROOT/"work"/(a.stem+".png")); dest.parent.mkdir(parents=True,exist_ok=True)
source=Path(a.source)
if source.resolve()!=dest: shutil.copy2(source,dest)
im=Image.open(dest); im.load()
base=[("q_daoist_character_pack_4096/06_thunder_caster_boy_transparent_4096.png","authoritative identity and anatomy"),("qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/E.png","east direction and camera"),("qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/W.png","west direction and camera"),("designs/jubaozhai-ui/02-characters.png","primary approved painted style")]
refs=[{"path":str(REPO/p),"role":role,"sha256":sha(REPO/p)} for p,role in base]
for p in a.extra: refs.append({"path":p,"role":"current generated pose and fixed proportions continuity reference; see exact prompt","sha256":sha(Path(p))})
raw=dest.read_bytes()
excerpts=[s.decode("ascii",errors="replace") for s in re.findall(rb"[ -~]{8,}",raw[:100000]) if b"gpt-image" in s or b"ChatGPT" in s or b"2026-10" in s]
ts=re.search(rb"2026-10-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z",raw[:100000])
generated=ts.group().decode() if ts else a.started
rec={"schema_version":1,"file":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"generatedAt":generated,"recordedAt":datetime.now(timezone.utc).isoformat(),"width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"native":{"width":im.width,"height":im.height,"perFrameWidth":im.width,"perFrameHeight":im.height},"tool":"image_gen.imagegen","route":"builtin","configSnapshot":json.loads((REPO/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":[r["path"] for r in refs]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具没有 model/quality 选择器，工具回执与C2PA通用gpt-image不披露具体型号/质量。","evidence":{"hostOutputPath":str(source),"resultFields":["image_url","output_hint"],"c2paPrintableExcerpts":excerpts,"callStartedAt":a.started,"generatedAtBasis":"embedded C2PA timestamp" if ts else "tool call start"},"prompt":a.prompt,"references":refs,"visualReview":a.review,"exported":False}
recpath=dest.with_name(dest.name+".generation.json")
if a.export:
 if im.width<1024 or im.width!=im.height or im.mode!="RGBA" or im.getchannel("A").getextrema()[0]!=0: raise ValueError("native square 1024+ transparent RGBA required")
 out=safe(ROOT/"runtime"/"cast"/a.direction/f"{a.frame:02d}.png")
 if out.exists(): raise FileExistsError(out)
 out.parent.mkdir(parents=True,exist_ok=True)
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
 outrec={"file":out.relative_to(ROOT).as_posix(),"sha256":sha(out),"width":1024,"height":1024,"format":"PNG","mode":"RGBA","derivedFrom":[{"file":rec["file"],"sha256":rec["sha256"],"generationRecord":recpath.relative_to(ROOT).as_posix()}],"native":rec["native"],"operation":"full canvas uniform Lanczos downsample; no cropping/mirroring/warping/bbox alignment","actualModel":None,"actualQuality":None,"unverifiedReason":rec["unverifiedReason"],"visualReview":a.review,"anchor":{"type":"fixed virtual ground/root provisional","x":512,"y":942,"normalizedUnityPivot":[0.5,0.08],"verified":False},"generatedAt":generated}
 out.with_name(out.name+".generation.json").write_text(json.dumps(outrec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 rec["exported"]=True; rec["exportPath"]=out.relative_to(ROOT).as_posix()
recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"native":im.size,"file":str(dest),"exported":rec["exported"],"generatedAt":generated,"sha256":rec["sha256"]},ensure_ascii=False))


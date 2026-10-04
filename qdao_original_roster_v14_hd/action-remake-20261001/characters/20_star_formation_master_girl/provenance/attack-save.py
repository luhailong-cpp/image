from pathlib import Path
import json,sys,hashlib,shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
job=json.loads(sys.stdin.buffer.read().decode('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
dest=(BASE/job["dest"]).resolve()
assert dest.is_relative_to(BASE/"generation"/"attack"),dest
assert not dest.exists() or sha(dest)==sha(job['source']),dest
dest.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(job["source"],dest)
im=Image.open(dest);im.load();alpha=im.getchannel("A")
receipt=BASE/job["receiptFile"]
receipt.write_text(json.dumps(job["receipt"],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
refs=[{"path":v,"role":job["roles"][i],"sha256":sha(v)} for i,v in enumerate(job["refs"])]
rec={"file":job["dest"],"sha256":sha(dest),"generatedAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"generatedAtMeaning":"本地接收保存时间；服务端时刻未披露","width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"tool":"image_gen__imagegen","route":"builtin","configSnapshot":json.loads((BASE.parents[3]/"config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":job["refs"]},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具无型号和质量选择器，回执未披露实际参数。","prompt":job["promptFile"],"promptSha256":sha(BASE/job["promptFile"]),"references":refs,"evidence":{"output_path":job["source"],"receipt":job["receiptFile"],"resultKeys":["image_url","output_hint"]},"review":{"status":job.get("status","pending_parent_visual_review"),"note":job["note"],"dynamicAcceptance":False},"pixelValidation":{"alphaExtrema":list(alpha.getextrema()),"alphaBBox":list(alpha.getbbox()),"solidBBoxAlpha8":list(alpha.point(lambda v:255 if v>=8 else 0).getbbox()),"nativeSize":list(im.size),"transformation":"Native PNG copied unchanged; no crop/scale/warp/mirror.","globalAnchorAcceptance":False}}
Path(str(dest)+".generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"file":job["dest"],"size":im.size,"mode":im.mode,"sha256":rec["sha256"],"solidBBoxAlpha8":rec["pixelValidation"]["solidBBoxAlpha8"],"status":rec["review"]["status"]}))



from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import hashlib,json
ROOT=Path(__file__).parent
CHAR=ROOT.parent.parent
p=ROOT/"native.png";im=Image.open(p);im.verify();im=Image.open(p);a=im.getchannel("A")
request=json.loads((ROOT/"request.json").read_text(encoding="utf-8"))
config=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
roles=["primary pose anatomy/depth reference: old walk E09 camera-near right leg leads","edit target: current E12 full sprite, preserve upper body/weapon","identity/costume/weapon details","primary approved painting style only"]
references=[{"file":path,"sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),"purpose":roles[i]} for i,path in enumerate(request["referenced_image_paths"])]
rec={"file":"generation/run-E-12-v2/native.png","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"generatedAt":datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),"generatedAtEvidence":"host returned PNG file modification time, recorded immediately after tool completion","width":im.width,"height":im.height,"format":"PNG","mode":im.mode,"tool":"image_gen.imagegen","route":"builtin","configSnapshot":config,"submittedParameters":{"model":None,"quality":None,"transparent_background":True,"referenced_image_paths":request["referenced_image_paths"]},"actualModel":None,"actualQuality":None,"evidence":{"receipt":"generation/run-E-12-v2/receipt.json"},"unverifiedReason":"宿主管理，工具没有model/quality选择器，结果未披露可核实型号与质量。","prompt":"generation/run-E-12-v2/prompt.txt","references":references,"editedFrom":{"file":"generation/run-E-12/native.png","sha256":references[1]["sha256"],"generationRecord":"generation/run-E-12/native.png.generation.json"},"review":{"status":"candidate-pending-parent-review","dynamicAcceptance":False,"nativeAlpha":a.getextrema()==(0,255),"nativeSizePass":im.width>=1024 and im.height>=1024,"visibleBBoxAlpha32":a.point(lambda x:255 if x>32 else 0).getbbox(),"observed":"Foreground leading thigh is redrawn larger and rear proximal thigh is more hidden by skirt; leg-depth success still requires side-by-side approval against E04. Front boot design also changed, so identity/detail review remains required."}}
(ROOT/"native.png.generation.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:rec[k] for k in ["file","sha256","width","height","mode","review"]},ensure_ascii=False))

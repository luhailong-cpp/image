from pathlib import Path
import json,hashlib
from PIL import Image
b=Path(r"D:/work/image/designs/creature-combat-20261005/pets/06-xiluo")
r=json.loads((b/"receipts/cast/E/10-attempt1.json").read_text(encoding="utf-8"))
p=Path(r["sourcePath"]); im=Image.open(p)
record={"status":"rejected_for_scale_drift","file":str(p),"native":{"width":im.width,"height":im.height,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()},"generatedAt":r["completedAt"],"configSnapshot":json.loads(Path(r"D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig")),"submittedParameters":{"model":None,"quality":None},"actualModel":None,"actualQuality":None,"unverifiedReason":"宿主管理，工具未披露","evidence":{"receipt":"receipts/cast/E/10-attempt1.json"},"prompt":"prompts/cast/E/10-attempt1.txt","references":r["arguments"]["referenced_image_paths"],"visualReview":"第10帧壳体比第09帧略缩小，定点重绘，不作为最终帧。"}
(b/"records/cast/E/10-attempt1.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")


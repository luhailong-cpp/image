from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
ROOT=Path(__file__).parent
now=datetime.now(timezone(timedelta(hours=-4))).isoformat()
config=json.loads(Path("D:/work/image/config/image-generation.json").read_text(encoding="utf-8-sig"))
for file in ROOT.glob("*.failure.json"):
 value=json.loads(file.read_text(encoding="utf-8"))
 value.update({"recordedAt":now,"timezone":"America/New_York","tool":"image_gen.imagegen","route":"builtin","configSnapshot":config,"actualModel":None,"actualQuality":None,"submittedModel":None,"submittedQuality":None,"outcome":"no-output-image","unverifiedReason":"宿主管理，工具未披露／无可核实元数据"})
 if file.name.startswith("attack-E-02"): value["request"]="attack-E-02.request.json"
 file.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
v2p=ROOT/"attack-E-06-v2.png.generation.json";v2=json.loads(v2p.read_text(encoding="utf-8"))
v1p=ROOT/"attack-E-06.png.generation.json";v1=json.loads(v1p.read_text(encoding="utf-8"))
v2["editedFrom"]={"file":"attack-E-06.png","sha256":v1["sha256"],"generationRecord":"attack-E-06.png.generation.json","sourceImageRetained":False,"sourceRemovalReason":"v2 selected as the sole current E06 candidate; prior image superseded after PNG/provenance integrity validation, historical text retained"}
v2p.write_text(json.dumps(v2,ensure_ascii=False,indent=2),encoding="utf-8")
v1.update({"status":"superseded-source-image-removed","retained":False,"supersededBy":"attack-E-06-v2.png","removedAt":now})
v1p.write_text(json.dumps(v1,ensure_ascii=False,indent=2),encoding="utf-8")
cleanup={"recordedAt":now,"deleted":[{"file":"attack-E-06.png","sha256":v1["sha256"],"reason":"Superseded by v2; no current preview or selected slot uses v1; historical generation reference retained."}],"retainedCurrentCandidates":["attack-E-01.png","attack-E-03.png","attack-E-06-v2.png","attack-E-09.png","attack-W-06.png"],"scope":"only attack-work"}
(ROOT/"cleanup.json").write_text(json.dumps(cleanup,ensure_ascii=False,indent=2),encoding="utf-8")

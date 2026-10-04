from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy");D=R/"provenance"/"attack"
for stem in ("E_frame_05_attempt_04","E_frame_07_attempt_02"):
 p=D/(stem+".png");rel=p.relative_to(R).as_posix()
 candidates=list((R/"frames"/"attack").glob("*/*.generation.json"))+list(D.glob("*retired*.generation.json"))
 matches=[]
 for gp in candidates:
  g=json.loads(gp.read_text(encoding="utf-8-sig"))
  if g.get("nativeSource",{}).get("path")==rel:matches.append((gp,g))
 if not matches:raise ValueError(stem)
 gp,g=matches[0];rec=dict(g)
 rec.update({"file":rel,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"width":1254,"height":1254,"operation":"native_image_generation","derivedFrom":[],"nativeSource":None,"recordedAt":datetime.now(timezone.utc).isoformat(),"referenceHashEvidence":"引用快照取自导出前register实际读取；不在目标被替换后重新哈希编辑前引用","boundExportRecord":gp.relative_to(R).as_posix()})
 (D/(stem+".png.generation.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(stem)


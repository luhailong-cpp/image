from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy").resolve()
paths=[R/"provenance/run/NW_01_attempt_01.png",R/"provenance/run/NW_01_attempt_02.png"]
for p in paths:
 if not p.resolve().is_relative_to(R):raise ValueError(p)
current=R/"frames/run/NW/frame_01.png"
rec=json.loads(current.with_suffix(".generation.json").read_text(encoding="utf-8-sig"))
if rec["nativeSource"]["path"]!="provenance/run/NW_01_attempt_03.png":raise ValueError("final not adopted")
if hashlib.sha256(current.read_bytes()).hexdigest()!=rec["sha256"]:raise ValueError("final SHA mismatch")
deleted=[]
for p in paths:
 if p.exists():
  deleted.append({"path":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"reason":"已被NW01 attempt03替代；非当前唯一在制稿；历史输入SHA和真实回执保留"})
  p.unlink()
(R/"provenance/run/NW_key_cleanup.json").write_text(json.dumps({"time":datetime.now(timezone.utc).isoformat(),"adoptedNative":"provenance/run/NW_01_attempt_03.png","adoptedExportSha256":rec["sha256"],"deleted":deleted,"policy":"2026-09-23用户素材保留：淘汰图不备份，保留来源文字","referenceAvailability":"历史输入路径可已删除或被正式新版本替代，历史SHA记录不代表当前像素"} ,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(deleted,ensure_ascii=True))


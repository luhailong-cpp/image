from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import subprocess,hashlib,json,sys
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
D=R/"provenance"/"run"
native=[];errors=[]
for p in sorted(D.glob("NE_*_attempt_*.png")):
 g=Path(str(p)+".generation.json")
 if not g.exists():
  r=subprocess.run([sys.executable,str(R/"tools"/"record_native.py"),str(p.with_suffix(""))],capture_output=True,text=True,encoding="utf-8")
  if r.returncode: errors.append({"file":p.name,"error":r.stderr+r.stdout})
 native.append(p)
selected={}
for p in sorted((R/"frames"/"run"/"NE").glob("*.generation.json")):
 g=json.loads(p.read_text(encoding="utf-8-sig")); selected[g["nativeSource"]["path"]]=g["sha256"]
retired=[]
for p in native:
 if p.relative_to(R).as_posix() in selected: continue
 if not Path(str(p)+".generation.json").exists(): continue
 retired.append({"file":p.relative_to(R).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"generationRecord":Path(str(p)+".generation.json").relative_to(R).as_posix(),"reason":"旧同腿姿态、换腿失败、杖首转面或短下杖已由当前独立新姿态替换；当前正式16帧已落盘，此文件不再作为后续生图输入"})
report={"createdAt":datetime.now(timezone.utc).isoformat(),"errors":errors,"selectedNativeCount":len(selected),"retiredCandidates":retired,"cleanupStatus":"planned_no_deletion_yet"}
(D/"NE_cleanup-plan-20261003.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"selectedNative":len(selected),"retired":len(retired),"errors":errors},ensure_ascii=False))



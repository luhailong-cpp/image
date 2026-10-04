from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
issues={3:"摆臂从后摆骤跳前摆；正在以W02定向重画过渡",4:"步相误回接触位，应为右脚后蹬/左膝前驱；正在重画",5:"应为右脚趾蹬地，旧稿呈宽跨腾空且杖首背盘变空心；正在重画",10:"疑似多余后摆衣袖/手臂，持物与近侧臂连接需修",11:"中支撑手臂过早到后摆极值，需中间回摆过渡"}
for n,reason in issues.items():
 p=R/"frames"/"run"/"W"/f"frame_{n:02d}.generation.json"
 if p.exists():
  data=json.loads(p.read_text(encoding="utf-8-sig"))
  data["review"]={"status":"needs_revision","automaticallyApproved":False,"note":reason,"reviewedAt":datetime.now(timezone.utc).isoformat(),"bindingSha256":data["sha256"]}
  p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("marked",list(issues))


from pathlib import Path
import json
from datetime import datetime,timezone
B=Path(__file__).parent
for name in ["REVIEW-CURRENT.json","selection-review.json"]:
 p=B/name;r=json.loads(p.read_text(encoding="utf-8"))
 r["updatedAt"]=datetime.now(timezone.utc).isoformat()
 r["trialTimingMs"]={"total":1200,"durations":[75]*16,"meaning":"Latest explicit user instruction: uniform75ms x16=1200ms; supersedes all older480/640/720/800 trials and phase weighting. Combat unchanged."}
 r["timingStatus"]="user_requested_uniform_1200ms; client not integrated"
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
p=B/"REVIEW-CURRENT.md";s=p.read_text(encoding="utf-8")
lines=s.splitlines();lines=[x for x in lines if not any(k in x for k in ["720","480","640","800","41,","81,"])]
s="\n".join(lines)+"\n\n最新用户要求：跑步16帧均匀75ms，整圈1200ms。当前预览不再提供480/640/720/800旧档，也不分相位权重；慢放、暂停、逐帧保留。历史生图prompt/receipt不改写，普攻30ms不变。\n"
p.write_text(s,encoding="utf-8")
print("Updated current E timing to uniform 75ms /1200ms")


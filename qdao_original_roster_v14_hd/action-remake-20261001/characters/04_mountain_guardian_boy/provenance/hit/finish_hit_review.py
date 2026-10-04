from pathlib import Path
import json,hashlib,subprocess,sys
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
p=R/"frames/hit/E/frame_06.png";s=p.with_suffix(".generation.json");j=json.loads(s.read_text(encoding="utf-8-sig"))
assert hashlib.sha256(p.read_bytes()).hexdigest()=="e3057b6dd3a28cedc0d2056e3c2c916ee2116e250f7992b672c159f6c59dd786"
j["review"]={"status":"visual_passed","automaticallyApproved":False,"scope":"static_single_frame_only","reviewedAt":datetime.now(timezone.utc).isoformat(),"note":"实际查看新原生与前帧，恢复E05头部大小；两脚收势、近右杖远左盾可读，杖首实心金盘修复。序列动态终验仍由根线程补核，不以单帧通过代替动态通过。"}
s.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
subprocess.run([sys.executable,str(R/"provenance/hit/build_hit_preview.py")],check=True)
for d in ("E","W"):
 refs=[{"path":f"frames/hit/{d}/frame_{n:02}.png","sha256":hashlib.sha256((R/f"frames/hit/{d}/frame_{n:02}.png").read_bytes()).hexdigest()} for n in range(1,7)]
 for name in ("contact.png","normal.gif","slow.gif"):
  p=R/f"provenance/hit/hit_{d}_{name}"
  data={"file":str(p.relative_to(R)).replace("\\","/"),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"derivedFrom":refs,"operation":"deterministic_preview_whole_canvas","modelGenerated":False,"updatedAt":datetime.now(timezone.utc).isoformat(),"normalFrameMs":40,"slowFrameMs":160}
  p.with_suffix(p.suffix+".generation.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print("hit E06 static review and current preview refreshed")


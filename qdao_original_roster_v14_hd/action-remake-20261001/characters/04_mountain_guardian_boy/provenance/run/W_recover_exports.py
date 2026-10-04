from pathlib import Path
from PIL import Image
import json,hashlib,io
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[2]
cases=[("W",4,"W_04_attempt_03","W_04_attempt_02.retired.generation.json"),("W",12,"W_12_attempt_02","W_12_attempt_01.retired.generation.json"),("NW",4,"NW_04_attempt_03","NW_04_attempt_01.retired.generation.json")]
for d,n,stem,prior in cases:
 p=R/"provenance/run"/(stem+".png"); m=json.loads(p.with_suffix(".png.generation.json").read_text(encoding="utf-8-sig"))
 dest=R/"frames/run"/d/f"frame_{n:02}.png"; side=dest.with_suffix(".generation.json")
 if dest.exists() or side.exists(): raise RuntimeError("slot no longer empty "+str(dest))
 assert hashlib.sha256(p.read_bytes()).hexdigest()==m["sha256"]
 old=json.loads((R/"provenance/run"/prior).read_text(encoding="utf-8-sig"))
 im=Image.open(p); assert im.mode=="RGBA" and min(im.size)>=1024
 b=io.BytesIO();im.resize((1024,1024),Image.Resampling.LANCZOS).save(b,format="PNG")
 ns={"path":str(p.relative_to(R)).replace("\\","/"),"sha256":m["sha256"],"width":im.width,"height":im.height,"format":"PNG","mode":"RGBA","alphaExtrema":list(im.getchannel("A").getextrema())}
 old.update({"sha256":hashlib.sha256(b.getvalue()).hexdigest(),"exportedAt":datetime.now(timezone.utc).isoformat(),"nativeSource":ns,"derivedFrom":[ns],"references":m["references"],"prompt":m["prompt"],"evidence":m["evidence"],"generationTimeEvidence":m["generationTimeEvidence"],"configSnapshot":m["configSnapshot"],"submittedParameters":m["submittedParameters"],"review":{"status":"candidate_pending_visual","automaticallyApproved":False},"recoveryNote":"成功原生及生成时参考SHA已存在；先前中断留下空导出槽。依据原生旁生成记录全画布等比重新导出，不另计AI生成。不以当前路径像素覆写生成时参考SHA。"})
 dest.write_bytes(b.getvalue());side.write_text(json.dumps(old,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(d,n,old["sha256"])


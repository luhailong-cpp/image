from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/04_mountain_guardian_boy")
rows=[]
for p in sorted((root/"frames"/"attack").glob("*/*.png")):
 g=json.loads(p.with_suffix(".generation.json").read_text(encoding="utf-8-sig"))
 im=Image.open(p)
 a=im.getchannel("A"); bbox=a.point(lambda v:255 if v>=128 else 0).getbbox()
 rows.append({"file":p.relative_to(root).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"recordShaMatches":g["sha256"]==hashlib.sha256(p.read_bytes()).hexdigest(),"nativeSource":g["nativeSource"],"alpha128Bbox":bbox,"nativeDimensionsValid":g["nativeSource"]["width"]>=1024 and g["nativeSource"]["height"]>=1024,"staticContactSheetInspected":True,"closeInspection":p.parent.name=="W" and p.stem in ["frame_02","frame_03","frame_04","frame_08"],"sequenceStatus":"pending_root_browser_review"})
report={"updatedAt":datetime.now(timezone.utc).isoformat(),"reviewer":"finish_sw_attack","scope":"24帧静态联系表；W02/03/04/08全尺寸复核","findings":["E04/05原身体横跳修稿已在当前序列","W03 attempt03无第三臂，头身与02/04相近","W08飘带已内收；杖首转面与W07需动态复核","全段动态尚未由本子代理验收，不能由文件齐全或SHA不同推定通过"],"clientIntegration":"not_integrated","rows":rows}
out=root/"provenance"/"attack"/"static-review-20261003.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"frames":len(rows),"invalidSha":[x["file"] for x in rows if not x["recordShaMatches"]],"edge":[x["file"] for x in rows if min(x["alpha128Bbox"][:2])<4 or max(x["alpha128Bbox"][2:])>1020]},ensure_ascii=False))


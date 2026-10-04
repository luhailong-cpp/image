from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).parent
notes=json.loads((B/"visual-notes.json").read_text(encoding="utf-8"))
slots=json.loads((B/"selection.json").read_text(encoding="utf-8"))["slots"]
rows=[]
for key,rel in sorted(slots.items()):
 p=B.parent/rel;im=Image.open(p);a=im.getchannel("A");rows.append(dict(slot=key,file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=list(im.size),mode=im.mode,bboxAlpha32=a.point(lambda a:255 if a>=32 else 0).getbbox(),review=notes.get(key),status="selected-static-check-pending-full-sequence"))
out=dict(updatedAtUtc=datetime.now(timezone.utc).isoformat(),selection="selection.json",ownTargetSlots=[4,9,10,11,12,13,14,15,16],selectedOwnCount=len(rows),frameDurationMs=75,cycleDurationMs=1200,uniformTiming=True,oldTimingOptionsRemoved=True,phaseWeighting=False,fixedTransform=dict(nativeCanvas=[1254,1254],scaledCanvas=[860,860],outputCanvas=[1024,1024],nativeVirtualRoot=[790,1155],directAlphaCompositeTranslation=[-30,150],basis="04 LEFT和12 RIGHT支撑关键平均地面约1155，骨盆投影x790；整个方向只用这一个试配准。"),hands="同一长枪红头左上、金尾右下；LEFT高/前握、RIGHT低/后握，两手连杆，不套竹弓空手动作。",reference="09当前runtime NE 已实际查看04/06/12/14，仅脚掌轴/膝踝/结构，不照搬帧号、身份、像素或根点。最新1200ms覆盖09旧720。",pending={"13":"v2 HTTP408留证，v3正修右脚抬跟；原版错误LEFT支撑拒绝。","14":"v2支撑侧已正确，但脚底1190比共同地面低35，v3正修膝踝与脚尖高度。","16":"原版脚底1188非真实离地，v2正通过屈膝抬踝修为下降腾空。"},frames=rows)
out["pending"]={n:v for n,v in out["pending"].items() if f"run/NE/{int(n):02d}" not in slots}
(B/"REVIEW-CURRENT.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
md="# NE 跑步当前源选择与实审\n\n按最新要求每帧75ms、16帧1200ms均匀播放；不分权重。当前仅选择已实际复核的负责槽，不把错误侧或低脚版本充数。\n\n"
for r in rows: md+=f"- {r['slot']} {r['file']}：{r['review']}\n"
md+="\n固定整方向配准：1254→860，直接合成1024时translation=(-30,150)，native虚拟根(790,1155)映射(512,942)。不逐帧最低脚对齐。完整16帧仍由统筹合并后正常/慢放复核。\n"
(B/"REVIEW-CURRENT.md").write_text(md,encoding="utf-8")
print(json.dumps({"selectedOwn":len(rows),"timing":1200,"frames":[r["slot"] for r in rows]}))


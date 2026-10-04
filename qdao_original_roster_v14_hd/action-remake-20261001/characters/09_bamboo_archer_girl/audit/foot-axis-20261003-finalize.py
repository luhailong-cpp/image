from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl")
g=root/"provenance/run-south"
source=json.loads((root/"audit/foot-axis-20261003/sources.json").read_text(encoding="utf-8"))["sources"]
current=json.loads((g/"current-qa-sources.json").read_text(encoding="utf-8"))
cm={(x["direction"],x["frame"]):x["sha256"] for x in current["frames"]}
for x in source:
 _,d,frame=x["slot"].split("/")
 p=root/f"runtime/run/{d}/{frame}.png"
 assert hashlib.sha256(p.read_bytes()).hexdigest()==x["sha256"]==cm[d,int(frame)]
 assert Image.open(p).mode=="RGBA" and Image.open(p).size==(1024,1024)
for d in ["W","S","SE"]:
 assert (g/f"{d}-contact-current.png").exists()
 for v in ["normal-720","slow-2880"]:
  for b in ["light","dark"]:
   assert Image.open(g/f"{d}-{v}-{b}.gif").n_frames==16
out=root/"audit/foot-axis-20261003.md"
text="""# 09 W/S/SE 脚尖轴与接地复核（2026-10-03）

本轮按最新用户更正独立判断09自身动作；07任何完整方向都不作为通过标杆。只读看过07 W/S/SE一般接触表，未读取或复用其像素用于生成，没有复制或镜像角色姿态。

实际看过09当前三套16帧完整接触表，另按统一原图坐标制作并查看48帧腿脚局部的分析表；SE03/04/11/12及疑似01/05/13/16又打开1024大图。六张分析表只是审查用裁切，不是游戏资源，也没有修改runtime。

## 结论

本轮未定位到足以确认、需要imagegen重新绘制的外八字错误，因此W/S/SE共48张冻结，图像及其生成记录SHA均不变。不能把「未确认外八字」扩大为整个动作已通过所有动态或接地检查。

- W：可见脚尖都沿屏左，前伸靴的鞋头在鞋跟左侧。01–03、09–11可辨支撑靴底和屈膝承重；04/12抬跟、后摆小腿接蹬离。后收脚的脚尖下垂属于脚踝俯仰，未看到向画面内外横拧的证据。
- S：前脚鞋头、鞋面中轴与胫骨基本在同一前进通道，左右脚没有向外分叉成八字。01–03及09–11的落脚可读为承重，04/12保留单侧支持与异侧抬膝。05–08和13–16的前脚露出鞋底属于抬脚/接触转换，不能因露底直接判外八字，也不应把所有这些帧标成已平踩地面。
- SE：前向脚鞋头沿右下，膝→踝→鞋面关系连续。03/11的前腿支撑与04/12的后腿抬跟蹬离可区别。01/05/13/16后收靴在小图中偏屏左，放大后可见屈膝后收、鞋跟抬高、鞋头向下的俯仰与透视；未找到鞋头相对同一靴子的鞋跟发生明确横向外拧的独立证据，不据此重画。其余12帧局部也未见明显外八字或膝踝反折。

接地结论限定在实际可见的承重与蹬离姿态。不同靴子俯仰、前后透视会改变最低像素，未以逐帧lowest-alpha自动贴地作为修复，也未把整段脚底强制对齐某一行。当前720/2880ms预览和current接触图来源48 SHA与runtime逐项相符；最终播放节奏/全套manifest由主线程统一处理。

## 当前48帧文件指纹

| 槽位 | 本轮处理 | SHA-256 |
|---|---|---|
"""
text+="\n".join(f"| {x['slot']} | 保留；无明确外拧证据 | {x['sha256']} |" for x in source)+"\n"
out.write_text(text,encoding="utf-8")
names=[]
for d in ["W","S","SE"]:
 names.append(f"{d}-contact-v2.png")
 for speed in ["normal","slow"]:
  for b in ["light","dark"]:names.append(f"{d}-{speed}-{b}-v2.gif")
names.append("W-contact.png")
for speed in ["normal","slow"]:
 for b in ["light","dark"]:names.append(f"W-{speed}-{b}.gif")
records=[]
for name in names:
 p=(g/name).resolve()
 assert p.parent==g.resolve() and p.suffix in [".png",".gif"]
 assert p.exists()
 records.append({"file":p.relative_to(root).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
log={"removedAt":datetime.now(timezone.utc).isoformat(),"reason":"Explicitly superseded previews. Current review/review-parts use current contact images and720/2880 GIFs; legacy W-review now points to current-review. Root confirmed manifest pngInventory is obsolete disk inventory and will be rebuilt.","runtimeChanges":0,"currentSourcesVerified":len(source),"deleted":records}
(root/"audit/foot-axis-20261003-preview-cleanup.json").write_text(json.dumps(log,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for name in names:(g/name).unlink()
print(json.dumps({"reviewedFrames":len(source),"runtimeChanges":0,"removedOldPreviews":len(names),"audit":str(out)},ensure_ascii=False))

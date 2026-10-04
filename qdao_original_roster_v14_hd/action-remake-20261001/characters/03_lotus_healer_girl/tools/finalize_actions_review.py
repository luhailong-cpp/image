"""Refresh this character's handoff from actual explicit selections, including gaps."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib, shutil

B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
overview=read(B/"review/all-actions-selection.json")
production=read(B/"review/production-status.json")
technical=read(B/"review/all-actions-technical-verification.json")
stamp=datetime.now(ZoneInfo("America/New_York")).isoformat()
inventory=[]; roots=[]; event_groups=[]; runtime=set(); table=[]; issue_sections=[]
for group in overview["groups"]:
    action,direction=group["action"],group["direction"]
    key=f"{action}-{direction}"
    for f in group["frames"]:
        inventory.append(dict(action=action,direction=direction,frame=f["frame"],file=f.get("file"),status="candidate_not_accepted" if f.get("file") else "missing"))
        if f.get("file"):
            if sha(B/f["file"])!=f["sha256"]: raise ValueError("export changed: "+f["file"])
            runtime.update([f["file"],f["generationRecord"]])
    ms=group.get("cycleMs")
    table.append(f"| {action} | {direction} | {group['present']}/{group['expected']} | {ms if ms else '—'} | {'候选待审' if group['present'] else '待补'} |")
    if not group.get("selection"): continue
    selection=read(B/group["selection"])
    runtime.add(group["selection"])
    roots.append(dict(action=action,direction=direction,nativeRoot=group["root"]["native"],nativeCanvas=group["root"]["nativeCanvas"],exportRootTopLeft=group["exportRoot"],exportCanvas=1024,normalizedTopLeft=[v/1024 for v in group["exportRoot"]],unityPivotBottomLeft=[group["exportRoot"][0]/1024,1-group["exportRoot"][1]/1024],productionCycleMs=None,trialCycleMs=ms,frameDurationsMs=[f["durationMs"] for f in group["frames"]],alignmentApplied=False))
    starts=[];elapsed=0
    for f in group["frames"]:starts.append(elapsed);elapsed+=f.get("durationMs") or 0
    events=selection.get("events",[])
    if selection.get("eventFrame"):
        frame=selection["eventFrame"]
        events=[dict(type={"hit":"impact","attack":"contact","cast":"release"}.get(action,"event"),frame=frame,timeMs=starts[frame-1],status="offline_candidate_not_client_event")]
    if action=="run" and direction=="E":
        events=[dict(type=name,frame=n,timeMs=starts[n-1],status="offline_candidate_not_client_event") for name,n in [("right_contact",16),("right_toe_off",6),("left_contact",9),("left_toe_off",13)]]
    event_groups.append(dict(action=action,direction=direction,cycleMs=ms,frameStartsMs=starts,events=events,status="offline_candidate_not_client_event" if events else "event_review_pending"))
    issues=list(selection.get("issues",[]))
    for f in group["frames"]:
        issues.extend(f"{direction}{f['frame']:02d}：{s}" for s in f.get("issues",[]))
    issue_sections.append(f"### {action} / {direction}\n\n"+("\n".join("- "+str(s) for s in issues) if issues else "本组暂无单独问题条目，仍须连播和客户端核验。"))

write(B/"review/slot-inventory.json",dict(updatedAt=stamp,target=196,candidate=overview["selectedExported"],accepted=0,missing=196-overview["selectedExported"],slots=inventory))
write(B/"review/root-and-timing.json",dict(schemaVersion=2,updatedAt=stamp,status="provisional_not_client_approved",transformation=dict(fullCanvasUniformDownscale=True,translation=[0,0],perFrameBBoxFit=False,lowestFootPin=False),runCycleMs=1200,runFrameMs=75,runMode="uniform",groups=roots))
write(B/"review/action-events.json",dict(schemaVersion=1,updatedAt=stamp,groups=event_groups))
write(B/"validation.json",technical)
shutil.copyfile(B/"review/selected-source-index.csv",B/"review/source-index.csv")
summary=f"当前已选入并导出 **{overview['selectedExported']}/196 帧** 1024×1024 RGBA 候选；库存另含尚未选入的原生在制稿。实际已有图片的槽位为 {production['presentSlots']}/196；重试版本不重复计作槽位。美术与动态尚未全部通过，客户端未接入/未运行。"
table_text="| 动作 | 方向 | 已选/目标 | 试播时长 ms | 状态 |\n| --- | --- | ---: | ---: | --- |\n"+"\n".join(table)
readme=f"""# 03 莲花医者 · 动作修复

{summary}

- [全部动作预览](preview/actions.html)：动作/方向切换，正常1×、0.25×、逐帧，128/256/512px；跑步统一1200ms一圈、16帧各75ms，已移除旧快档。缺帧保留空槽。
- [竹弓少女指定参照](../09_bamboo_archer_girl/preview/index.html)：只读对照同方向姿态；保留莲花少女外形与持物。旧index/new-run入口自动进入当前全部动作。
- [逐组真实进度](review/production-status.json)、[当前选帧](review/all-actions-selection.json)、[来源与SHA](review/source-index.csv)、[合并交接](MERGE_HANDOFF.md)。

{table_text}

浏览器入口需由本地HTTP服务读取JSON。本次服务为 http://127.0.0.1:8873/ ，根目录 D:/work/image；本角色入口为 preview/actions.html。generation中选用的原生图仍是当前在制源，candidate为完整画布统一缩小的候选，不是通过状态。没有镜像、复制、扭曲或插值补帧，没有逐帧最低脚贴地、独立包围盒适配或整体移图。

跑步节奏与落地姿势分别核验；受击240ms、普攻360ms、施法720ms保持各自动作时长。内置图像工具未披露实际型号/质量，逐图记录为null，配置目标不当作实际调用证明。
"""
(B/"README.md").write_text(readme,encoding="utf-8")
handoff=f"""# 03 莲花医者 · 本机交接

更新：{stamp}。仅写本角色目录；未操作Git、共享配置、其他角色或客户端。

{summary}

{table_text}

## 预览与来源

[全部动作](preview/actions.html)读取[选帧清单](review/all-actions-selection.json)，每槽指向真实独立原生来源及SHA。导出只做完整原生画布1254→1024等比缩小，translation=(0,0)，保留透明度；没有镜像、复制、形变或插值填槽。旧E01/E05的复用保留旧来源记录，旧512 walk未冒充新的高清run。

逐图实际模型和质量未披露即null，逐图prompt/job/receipt/generation记录保存目标、实际参数、回执与SHA。[source-index.csv](review/source-index.csv)列出当前选中来源；[技术检查](review/all-actions-technical-verification.json)仅证明文件/尺寸/唯一性，不能替代动作验收。

## 根点、时长与事件

[root-and-timing.json](review/root-and-timing.json)逐组记录固定原生根点、1024导出根点、规范化pivot及逐帧时长；这些是离线诊断值，尚未在客户端采用。透视远近脚允许不同屏幕高度，不能通过逐帧最低脚移动伪造落地。

[action-events.json](review/action-events.json)记录已有实图候选的接触/离地、受击、普攻接触与施法释放帧，缺失的事件明示待核查。跑步离线正常1×为1200ms=16×75ms；正式客户端周期仍null；受击/普攻/施法保持240/360/720ms。

## 当前待核查项

以下按本次选帧的真实问题记录汇总；包含待连播核对项，不将全部问题等同于确定错误。后续修图应先检查当前source/hash，避免按淘汰版本重复修改。

"""+"\n\n".join(issue_sections)+"\n\n## 合并与保留\n\n确认当前所需来源与1024候选完整后，按根AGENTS规定清理已淘汰图片，保留逐图文字证据和SHA；旧目录只读。另一电脑合并仅取本角色目录所需成品及配套记录。当前已只读确认 D:/work/mmorpg-client 存在；本任务仍只修改本角色素材，未接入或运行游戏内滑步/命中/释放验证。\n"
(B/"MERGE_HANDOFF.md").write_text(handoff,encoding="utf-8")
runtime.update(["manifest.json","validation.json","README.md","MERGE_HANDOFF.md","review/all-actions-selection.json","review/all-actions-technical-verification.json","review/production-status.json","review/slot-inventory.json","review/root-and-timing.json","review/action-events.json","review/source-index.csv","preview/actions.html","preview/actions.js","preview/new-run.html","preview/new-run.js"])
write(B/"review/delivery-integrity.json",dict(checkedAt=stamp,status="candidate_not_accepted",selectedExported=overview["selectedExported"],files=[dict(path=p,sha256=sha(B/p)) for p in sorted(runtime)]))
print(json.dumps(dict(selectedExported=overview["selectedExported"],nativeSlots=production["presentSlots"],handoff="MERGE_HANDOFF.md",missingSelected=196-overview["selectedExported"])))

from pathlib import Path
from PIL import Image
import json,hashlib,re
B=Path(__file__).parent
raw=json.loads((B/"selection.json").read_text())["slots"]; selection={d:{str(n):Path(raw[f"attack/{d}/{n:02d}"]).name for n in range(1,13)} for d in ["E","W"]}
notesE=["v2严格E侧起势，修正双眼正面相机；与E11/12固定头身尺度。","v2后腿承重、前腿卸重、双肘回收；蓄力明确。","v2后膝更深、重心更低；最大蓄力明确。","后蓄切入前弓，E03至E04位移较急待实播。","前刺伸出，后腿直、前腿弯，持枪清楚。","v2接触关键帧，枪双端清楚；右枪尖近边。","v2完整枪尖，主alpha右界1226，留28px。","回收初段，与E07差异较小待实播。","抬枪回收，双手未换序，站距开始回收。","双脚收近、枪斜抬；相机角度稍变。","回到较高持枪位置，双脚仍分开。","v4沿E11相同头身尺寸与屈膝站距，仅闭口/收稳枪发；v2/v3站立高度过大弃用。"]
notesW=["起势，双手枪双端清楚。","后腿加载、前腿卸重，实际最大蓄力。","实际进入前弓起刺，不是最大蓄力，采用启动相位。","前刺推进，鞋底偏高需方向整体配准复核。","接触前推进，双手分离明确。","v2侧面接触、双手握枪与两脚支撑明确；与W05同基线，W方向共同配准，不单帧下移。","跟进前刺，左枪尖完整但近边。","折肘回收，持枪左右顺序不变。","枪斜抬、后脚收回。","新补槽：直立回收、枪斜上左。","收枪近起势，面部略偏正面。","收势，手枪对应保持；与W01闭合待实播。"]
rows=[]
for d in ["E","W"]:
 for n in range(1,13):
  fn=selection[d][str(n)];p=B/fn;im=Image.open(p);a=im.getchannel("A")
  r=dict(direction=d,frame=n,file=fn,durationMs=30,event="contact" if n==6 else None,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),mode=im.mode,visibleBBoxAtAlpha32=a.point(lambda x:255 if x>=32 else 0).getbbox(),generationRecord=fn+".generation.json",status="selected-native-candidate-pending-sequence",review=(notesE if d=="E" else notesW)[n-1])
  rows.append(r)
  rp=B/r["generationRecord"];rec=json.loads(rp.read_text(encoding="utf-8"));rec.update(selection="current",visualReview=r["review"],status=r["status"]);rp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
out=dict(character="10_crimson_spear_girl",action="attack",targetFrames=24,generatedUniqueSlots=24,selectedNativeFrames=24,visuallyApprovedSequence=False,formalExportedFrames=0,rootAnchorTarget=[512,942],runtimeCanvasTarget=[1024,1024],nativeCanvas=[1254,1254],frameDurationMs=30,segmentDurationMs=360,contactFrame1Based=6,transform=None,transformStatus="Root owner applies common full-canvas scale and direction registration; no bbox fitting or lowest-foot snapping",clientIntegrated=False,clientTested=False,blockedBy=None,frames=rows)
(B/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
js=(B/"preview.js").read_text(encoding="utf-8")
lines=js.splitlines();lines[1]="const slots = "+json.dumps(selection)+";";lines[2]="const reviews = "+json.dumps({r["file"]:r["review"] for r in rows},ensure_ascii=False)+";"
(B/"preview.js").write_text("\n".join(lines),encoding="utf-8")
html=(B/"preview.html").read_text(encoding="utf-8").replace("5 / 24 个槽位有原生候选；美术通过 0，正式导出 0。空槽保留空白，不跳过、不复制补齐。","24 / 24 原生候选；E02/E03/E06/E07/E12 用 v2。整段尚未放行，正式导出 0。")
(B/"preview.html").write_text(html,encoding="utf-8")
report="# 普攻选用与审阅 · 2026-10-03\n\n24/24原生候选齐全。E01/E02/E03/E06/E07/W06选v2，E12选v4，其余原版本。1254×1254 RGBA独立生图。逐图配置目标与实际null分开记录。每帧30ms，每段360ms；跑步降速意见不应用于普攻。\n\n"
report+="\n".join(f"- {r['direction']}{r['frame']:02d} {r['file']}：{r['review']}" for r in rows)
report+="\n\n未做最终根点配准或客户端验收。E01侧相机、E12尺寸突变、W06侧面握枪均已实际修订；仍须整段动态与共同方向配准。根点由骨盆投影与方向共同虚拟地面确定，禁止最低脚贴地。\n"
for f in ["REVIEW.md","README.md","MERGE_HANDOFF.md"]:(B/f).write_text(report,encoding="utf-8")
print(json.dumps({"selected":24,"mainEdgeTouch":[r["file"] for r in rows if any(v in (0,1254) for v in r["visibleBBoxAtAlpha32"])]}))


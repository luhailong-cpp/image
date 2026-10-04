from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).parent
slots=json.loads((B/"selection.json").read_text(encoding="utf-8"))["slots"]
phasesE=["起势","后腿加载蓄力","最深蓄力","向前切入","前刺推进","全伸前刺/接触候选","跟进保持","初始收回","抬枪收势","站距收回","收稳近起势","收势闭合"]
phasesW=["起势","最大后载蓄力","已开始向前切入","前刺展开","前刺接近全伸","全伸前刺/接触候选","跟进保持","折肘收回","抬枪收势","直立回收","近起势","收势"]
rows=[]
for key,rel in slots.items():
 _,d,n=key.split("/"); n=int(n); p=B.parent/rel; im=Image.open(p); bb=im.getchannel("A").point(lambda a:255 if a>=32 else 0).getbbox()
 note=("后靴已局部修成鞋跟左/鞋尖右，膝踝与进攻E方向一致。" if d=="E" else ("后靴已局部修成鞋跟右/鞋尖左。" if n in [2,6] else "鞋帽虽有透视朝下，鞋跟仍在右、鞋尖偏左；未因缩短透视误判成外八。"))
 if d=="E" and n==6: note+=" v6枪尖完整，alpha32右界1247留7px；v4/v5触边弃用。"
 if d=="E" and n==11: note+=" v1头身意外放大已拒绝；v2恢复原头位与尺寸。"
 if d=="W" and n==2: note+=" v1仍朝右已拒绝；v2鞋跟右、鞋尖左清楚。"
 if d=="E" and n==3: note+=" ground-v3后脚鞋跟左、鞋头右；原生鞋底约1123，深蹲蓄力，双手和整枪保留。"
 if d=="W" and n==3: note+=" ground-v2双鞋跟右、鞋头左，鞋底1090；接新W04约1101–1114，只余11–24nativepx过渡差，不再微调重画。"
 if d=="W" and n==9: note+=" ground-v1鞋底1141，较共同面1120低21nativepx，收枪恢复站姿；保留透视容差。"
 if d=="W" and n==11: note+=" ground-v1两靴底1138，原1159/1154单帧下沉改善约22nativepx，残差18nativepx保留；枪尖完整左界7，双手/鞋轴W正确。头发顶部约上移27nativepx，须结合收势动态看，不为小漂移继续重画。"
 if d=="W" and n in [4,5,6,7,8]: note+=" 本目录保留原选源，接地替换由attack-W-grounding-work负责，总导出须以该目录明确selection为优先；此处不声称旧源接地通过。"
 phase=(phasesE if d=="E" else phasesW)[n-1]
 rows.append(dict(slot=key,file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=list(im.size),bboxAlpha32=bb,phaseObserved=phase,footAxisReview=note,handReview="两手与长枪杆连接，左高/前握向红枪头，右低/后握向金尾；没有第三手。",durationMs=30,event="contact_candidate" if n==6 else None,status="selected_static_foot_axis_checked_sequence_grounding_pending",generationRecord=rel+".generation.json"))
 recp=Path(str(p)+".generation.json");rec=json.loads(recp.read_text(encoding="utf-8"));rec.update(selection="current",visualReview=note,observedPhase=phase,status="selected_static_foot_axis_checked_sequence_grounding_pending");recp.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding="utf-8")
transforms={"E":{"nativeVirtualRoot":[670,1140],"scale":860/1254,"scaledCanvas":[860,860],"outputCanvas":[1024,1024],"alphaCompositeTranslation":[53,160],"basis":"骨盆投影约native x670，起收势支撑带约1140；E03修正后鞋底1123，保持深蹲加载。仅整方向固定试配准。"},"W":{"nativeVirtualRoot":[746.3,1120],"scale":860/1254,"scaledCanvas":[860,860],"outputCanvas":[1024,1024],"alphaCompositeTranslation":[0,174],"basis":"共同支撑带约1120；原估计x770对应-16会截完整枪尖，修正为全方向x0，虚拟根x746.3。不逐帧挪枪或贴脚；W04–08由独立接地目录替换。"}}
out=dict(character="10_crimson_spear_girl",action="attack",updatedAtUtc=datetime.now(timezone.utc).isoformat(),selectedNativeFrames=24,visuallyApprovedSequence=False,shoeAxisStaticChecked=True,clientIntegrated=False,clientTested=False,frameDurationMs=30,segmentDurationMs=360,contactFrame1Based=6,contactEvidence="两方向06均全伸直枪与弓步，适合作为接触候选；05–07接近全伸平台，未声称06是唯一最远枪尖。枪头实际完整，战斗速度未放慢。",fixedDirectionRegistrationProposal=transforms,blockingVisualIssues=["总导出仍需将attack-W-grounding-work已选W04–08覆盖本目录旧源，再作整段动态检查。"],remainingReview=["E02→03深蹲加载有明显头髋下降，应在30ms原速整段确认连贯。","W03接新W04的鞋底差为11–24nativepx，W09约21nativepx低于共同面；保留透视与承重容差，不逐帧平移。"],latestActionReference="09_bamboo_archer_girl current runtime accepted by user as action reference; not imported identity or bow motion.",frames=rows)
(B/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
(B/"REVIEW-CURRENT.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
report="# 赤枪少女普攻当前选择\n\n24/24独立原生1254方图均已明确选择，双脚方向静态复核完成；尚未声称整段动态和地面通过。每帧30ms、每向360ms不变。\n\n"
report+="\n".join(f"- {r['slot']} → {r['file']}：{r['phaseObserved']}；{r['footAxisReview']}" for r in rows)
report+="\n\n## 固定整方向配准建议\n\n1254整画布统一缩到860，再直接alpha_composite至1024。E总translation=(53,160)，native虚拟根(670,1140)；W总translation=(0,174)，native虚拟根(746.3,1120)。原W x=-16会裁枪尖，已撤回，改全方向x=0。配准是整方向常量，不是逐帧最低脚贴地。E03 ground-v3鞋底1123且双鞋头E；W03 ground-v2鞋底1090，接新W04约1101–1114仅余11–24nativepx；W09 ground-v1鞋底1141，较共同面1120低21nativepx。保留合理透视与承重差，不再为微小差重复重画。E02→03深蹲头髋下降需在30ms原速串联确认。W04–08由attack-W-grounding-work独立修复，总导出须使用其明确选择；本目录旧源保留但不作为接地通过结论。\n\n06接触事件：两向06均为全伸直枪和弓步，可作contact候选；05–07全伸平台接近，06不是独占枪尖最远的一帧。E06v6右尖完整留7px，当前24张alpha32无主轮廓触边、无相同SHA，几何检查不代替动态验收。\n\n逐图generation保留配置目标GPT Image2.5 Sunburst/max，实际参数和返回model/quality均null。09竹弓少女为用户最新动作参照；月影不再作为整套正确证据。\n"
for f in ["REVIEW.md","README.md","MERGE_HANDOFF.md"]:(B/f).write_text(report,encoding="utf-8")
js=(B/"preview.js").read_text(encoding="utf-8");lines=js.splitlines();lines[1]="const slots = "+json.dumps({d:{str(n):Path(slots[f"attack/{d}/{n:02d}"]).name for n in range(1,13)} for d in ["E","W"]})+";";lines[2]="const reviews = "+json.dumps({Path(r["file"]).name:r["phaseObserved"]+"；"+r["footAxisReview"] for r in rows},ensure_ascii=False)+";";(B/"preview.js").write_text("\n".join(lines),encoding="utf-8")
print(json.dumps({"selected":24,"groundingOverrideRequired":["W04","W05","W06","W07","W08"],"transitionsFixed":["E03","W03","W09"],"translations":transforms},ensure_ascii=True))


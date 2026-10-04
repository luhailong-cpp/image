from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
NOW=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
NOTES={
"W":[
"前腿伸向左，后腿屈起；盾前杖后，手臂可连到肩。",
"前侧支撑靴平压，后腿收起；与01可区别，不是平移。",
"支撑靴转到身体下方，另一腿通过；双手仍各持原物。",
"前摆膝抬起、后脚跟离地，杖臂进入前摆；需动态关注03→04幅度。",
"后脚蹬离，前膝抬高；盾向后、杖向前。",
"明显腾空跨步，前靴张开、后膝弯曲；整根直杖完整。",
"腾空下降，前腿进一步伸出、后腿屈曲；不同于06。",
"落地前伸脚，前后脚不并拢；盾后杖前。",
"异侧脚接触相，另一腿后收；与01的腿和持物摆臂相反。",
"异侧支撑压低，后腿回收；非重复09。",
"支撑腿在髋下、另一脚向前收；右握杖手已靠近胸前过渡。",
"双腿交换中段，右手移到腰侧过渡；完整下杆、金尖和实心背盘。",
"另一侧蹬离、前腿驱动；已补回被衣摆遮挡后重现的下杖。",
"第二腾空半周期，盾前杖后；吊穗已向内摆，画布内完整。",
"第二腾空下降；已补全下杆和金尖，并将吊穗收回画布。",
"返回第一接触前的伸脚姿态；左右腿可分，完整长杖。"],
"NW":[
"已反转旧同腿姿态：画面左靴向后露底、右靴向前；盾左、杖右。",
"右靴平放支撑，左跟屈起回收；与01区别明显。",
"右靴落在髋下支撑，左腿通过；修掉旧双脚同时腾空。",
"左膝向前、右后脚跟抬起；右臂在自身右肩侧前摆，需动态关注03→04。",
"第一蹬离相：左膝驱动、右后踝伸展；右手仍在画面右侧，未跨头。",
"第一腾空：两膝弯曲且双靴高度不同；已修正误置左侧的右手和断轴长杖。",
"腾空下降、左腿在纵深前伸；保留正确左右手并补全下长杖。",
"左脚落地前伸；双脚分开，右臂屈曲持杖、盾在画面左侧。",
"左靴明确平落，右靴在后露底；和01组成相反半周期，未换手。",
"左支撑压低、右后跟收起；左右靴不重复09。",
"左支撑中段，右膝向前回收；盾/杖手未对调。",
"左脚跟抬高，右腿通过；已补全直杖下杆，吊穗收回画布。",
"左脚蹬离、右膝驱动；已改变旧同腿稿，吊穗完整。",
"第二腾空：左后底可见、右腿屈收；完整长杖与金尖。",
"第二腾空下降：左脚在后、右脚前伸；杖尾完整，吊穗向内。",
"回到右脚落地前，左后靴底与右前靴清楚；与01衔接待动态终验。"]}
for d in ("W","NW"):
 rows=[]
 for n in range(1,17):
  p=ROOT/"frames"/"run"/d/f"frame_{n:02d}.png";mp=p.with_suffix(".generation.json")
  j=json.loads(mp.read_text(encoding="utf-8-sig"));im=Image.open(p)
  assert im.size==(1024,1024) and im.mode=="RGBA"
  assert j["sha256"]==sha(p)
  bbox=im.getchannel("A").point(lambda a:255 if a>32 else 0).getbbox()
  note=NOTES[d][n-1]
  j["review"]={"status":"visual_passed","scope":"static_single_frame_only","automaticallyApproved":False,"reviewedAt":NOW,"reviewedSha256":sha(p),"observation":note,"dynamicAcceptance":"pending_parent_normal_and_quarter_speed_review","note":"已实际查看正式PNG/逐帧接触表。尺寸/数量/哈希不是通过依据。静态通过不代表落地感、速度与相邻帧跳变的动态终验通过。"}
  j["frameDurationMs"]=None
  j["runTiming"]={"legacyFrameDurationMs":30,"legacyLoopMs":480,"status":"trial_pending_dynamic_acceptance","trialLoopMs":[640,720,800],"previewLoopMs":720,"previewFrameMs":45,"quarterSpeedLoopMs":2880,"gifNote":"10ms粒度的720ms GIF以40/50ms交替；浏览器可用精确45ms。","clientApprovedLoopMs":None}
  save(mp,j)
  rows.append({"file":str(p.relative_to(ROOT)),"sha256":sha(p),"size":list(im.size),"mode":im.mode,"alphaExtrema":list(im.getchannel("A").getextrema()),"alphaAbove32Bounds":list(bbox),"staticObservation":note,"reviewScope":"static_single_frame_only"})
 report={"reviewedAt":NOW,"direction":d,"frames":rows,"staticVisualReviewed":16,"dynamicAcceptance":"pending_parent_normal_and_quarter_speed_review","clientIntegration":"not_integrated","watchTransitions":(["W03→W04持杖臂过渡","W11→W12持杖臂回摆","W16→W01循环接缝"] if d=="W" else ["NW03→NW04右臂抬升幅度","NW05→NW06头身比例","NW16→NW01循环接缝"]),"rootAnchorStatus":"declared_layout_target_not_pixel_verified","modelEvidence":{"configTarget":"GPT Image 2.5 Sunburst / max","actualModel":None,"actualQuality":None}}
 save(ROOT/"provenance"/"run"/f"{d}_review_20261003.json",report)
 lines=[f"# 山岳守卫 {d} 跑步手脚修正","",f"当前16/16帧已生成并导出，已完成逐帧静态查看。动态落地感、相邻跳变与循环接缝交主窗口用正常和0.25倍速终验；不将帧数齐全或静态通过冒作完整动作通过。","",
 "每帧为独立内置AI生成/编辑的原生图，全画布等比导出1024×1024 RGBA。没有镜像、复制姿态、骨骼扭曲、插值补帧、逐帧bbox贴地或脚底自动对齐。rootAnchor(512,928)仍为布局目标声明，未冒称像素验收。",
 "","实际查看并传入本机已提交身份画像、相应idle与designs/jubaozhai-ui/02-characters.png风格参考；所有修改只使用本批本机新稿作编辑目标。没有使用旧run-correction/combat在制图或另一电脑未提交素材。",
 "","已提供640/720/800ms三档试播；normal采用720ms候选，slow采用其0.25倍。480ms旧值已撤为旧基线，正式客户端时长未批准。GIF用40/50ms交替实现720ms，不复制或插值姿态。",
 "","目标GPT Image 2.5 Sunburst / max；宿主内置没有model/quality选择器，实际提交和返回型号/质量都未确认（null）。逐图记录区分目标、参数、返回、来源SHA和提交/完成时间。",
 "","| 帧 | 本轮实际静态观察 |","|---|---|"]
 lines += [f"| {d}{n:02d} | {NOTES[d][n-1]} |" for n in range(1,17)]
 lines += ["","当前预览：",f"- provenance/run/{d}_contact.png",f"- provenance/run/{d}_trial640.gif、{d}_trial720.gif、{d}_trial800.gif",f"- provenance/run/{d}_normal.gif、{d}_slow.gif",f"- 逐帧SHA绑定审查：provenance/run/{d}_review_20261003.json","","本机没有客户端，未接入。无Git暂存/提交/推送或切分支。"]
 (ROOT/f"RUN_{d}_NOTES.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"staticReviewed":32,"dynamic":"pending_parent_review","client":"not_integrated"},ensure_ascii=False))


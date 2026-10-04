from pathlib import Path
from PIL import Image,ImageSequence
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
NOW=datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
obs=[
"第一半周期前靴后跟触地、脚尖稍抬，后靴蹬离；右杖后摆，左盾前摆，手脚可分。",
"前侧靴完整平掌承重、膝下压，后脚屈起；与01的触地倾角明确区别。",
"支撑靴移至髋下、另一膝通过，杖臂向中位回收；单根全长杖，双脚不粘连。",
"已真实AI缩小前摆手极位，右肘屈曲、握杖手靠近胸侧；原前膝驱动与后脚蹬离腿相保留。",
"第一蹬离相，前膝驱动、后踝伸展；右杖前摆，左盾后摆，完整长杖。",
"第一腾空，相隔的两靴都抬起，后腿屈曲、前腿开始伸展；无多肢。",
"腾空下降，前腿进一步伸出、后踝回收；与06腿形不同。",
"落地前伸脚，前靴翘起、后腿收回；持杖臂与盾臂不换手。",
"第二半周期前靴后跟接触、后靴即将离地；和01具有相反的持物摆臂与髋部腿遮挡。",
"已真实AI降低承重靴并抬高后收靴：明确一只平掌支撑、另一腿屈膝离地；修掉原双脚近乎同高的假双支撑。",
"父线程已去掉重复杖，本轮仅修盾面由外面突然朝镜头改为内背面及握把；单根直杖、髋下支撑脚保留。",
"已真实AI将回摆手收近腰侧过渡，继而补回完整下长杖和金尖；前膝/后脚腿相保留。",
"第二蹬离相，右杖后摆、左盾前摆，前膝抬起，后脚离地。",
"第二腾空，两脚离开接触高度且清楚分开，前膝驱动、后膝屈曲。",
"第二腾空下降，前小腿伸展、后脚折回；长杖整杆可追踪。",
"下一次触地前伸脚，前靴翘尖、后腿弯曲；16→01仍交动态接缝验收。"]
rows=[]
for n in range(1,17):
 p=ROOT/"frames/run/E"/f"frame_{n:02d}.png";mp=p.with_suffix(".generation.json")
 j=json.loads(mp.read_text(encoding="utf-8-sig"));im=Image.open(p)
 assert im.size==(1024,1024) and im.mode=="RGBA" and sha(p)==j["sha256"]
 ns=j["nativeSource"];np=ROOT/ns["path"];assert np.exists() and sha(np)==ns["sha256"]
 j["review"]={"status":"visual_passed","scope":"static_single_frame_only","automaticallyApproved":False,"reviewedAt":NOW,"reviewedSha256":sha(p),"observation":obs[n-1],"dynamicAcceptance":"pending_parent_normal_and_quarter_speed_review","note":"实际查看16张正式PNG及重建接触表。静态通过不是动态落地感、运动连续性或客户端接入通过。"}
 save(mp,j)
 rows.append({"file":str(p.relative_to(ROOT)),"sha256":sha(p),"size":list(im.size),"mode":im.mode,"alphaExtrema":list(im.getchannel("A").getextrema()),"alphaAbove32Bounds":list(im.getchannel("A").point(lambda a:255 if a>32 else 0).getbbox()),"nativeSource":ns["path"],"nativeSha256":ns["sha256"],"nativeRetained":True,"staticObservation":obs[n-1]})
gifs=[]
for speed,total in (("normal",720),("slow",2880),("trial640",640),("trial720",720),("trial800",800)):
 p=ROOT/"provenance/run"/f"E_{speed}.gif"
 with Image.open(p) as im:durs=[f.info["duration"] for f in ImageSequence.Iterator(im)]
 assert len(durs)==16 and sum(durs)==total
 gifs.append({"file":str(p.relative_to(ROOT)),"frames":16,"totalMs":sum(durs),"sha256":sha(p)})
save(ROOT/"provenance/run/E_review_20261003.json",{"reviewedAt":NOW,"direction":"E","frames":rows,"staticVisualReviewed":16,"dynamicAcceptance":"pending_parent_normal_and_quarter_speed_review","clientIntegration":"not_integrated","watchTransitions":["E03→E04前摆过渡","E09→E10→E11单脚支撑与后腿回收","E11→E12→E13回摆过渡和杖旋转","E16→E01循环接缝"],"groundingNote":"支撑/腾空按膝踝姿态及靴底读取；rootAnchor仅布局目标，尚未宣称像素级固定脚底基线通过。没有bbox/脚底贴地。","previews":gifs,"timingOwnership":"根线程统一；本次未改写任何frameDurationMs或历史提交模型参数。","modelEvidence":{"configTarget":"GPT Image 2.5 Sunburst / max","actualModel":None,"actualQuality":None}})
lines=["# 山岳守卫 E 跑步手脚复核","",
"2026-10-03：16/16帧已实际逐张查看，并完成定点AI修正。静态手脚/持物检查通过；正常、0.25倍速的落地感、相邻跳变及首尾连续性仍待主窗口动态终验。当前选中nativeSource全部保留且SHA已核对。",
"",
"本轮只改E04、E10、E11、E12：E04缩小前摆极位；E10承重靴下放与后收脚抬起；E11保留根线程已修好的单杖，仅修盾的内外表面跳变；E12手收近腰侧，并补回首轮被缩短的下杖。其余帧保留经实看的本机本批姿态。",
"",
"真实传入并查看身份画像、E idle和designs/jubaozhai-ui/02-characters.png；本轮新稿作局部编辑目标。没有使用旧run-correction/combat在制图或另一电脑未提交素材。原生1254方RGBA，整画布等比导出1024方RGBA，无镜像、复制姿态、插值、扭曲、逐帧bbox或脚底贴地。目标rootAnchor(512,928)没有冒称像素验证。",
"",
"配置目标GPT Image 2.5 Sunburst / max；内置没有型号/质量选择器，实际提交及实际返回为null未确认。逐图prompt/submission/receipt和来源SHA已保存。未调用收费API/CLI，未接入客户端，无Git操作。",
"",
"| 帧 | 实际静态观察 |","|---|---|"]
lines.extend(f"| E{n:02d} | {obs[n-1]} |" for n in range(1,17))
lines+=["","当前预览：provenance/run/E_contact.png、E_normal.gif、E_slow.gif、E_trial640.gif、E_trial720.gif、E_trial800.gif。normal为720ms试播，slow为其0.25倍；640/720/800仅供动态选时，最终客户端值由主窗口统一确认。历史frameDurationMs未在本分工改写。",
"","逐帧SHA绑定审查见provenance/run/E_review_20261003.json。动态重点：03→04、09→10→11、11→12→13及16→01。当前仅静态通过，不能因为16槽齐全就宣告完整动作验收通过。"]
(ROOT/"RUN_E_NOTES.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"staticReviewed":16,"nativeVerified":16,"gifChecks":5,"dynamic":"pending_parent_review"},ensure_ascii=False))


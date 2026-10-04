import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
rows=[]
phases={
1:"已重绘右靴平底接触承重，左腿后屈；与16可连续追踪同一右脚。",
2:"已重绘为右脚连续承重、左脚后屈，纠正提前换脚。",
3:"右腿承重、左腿经过；仍需在真实地面参考中核验负重。",
4:"右脚后伸蹬离；已重画左弓臂后摆、右空手前摆。",
5:"短暂腾空，双脚脱离支撑；左右肩肘反向摆动已重画。",
6:"腾空转向下一步；持弓后摆与空手前摆可读。",
7:"已重绘左脚接触、右脚后收，纠正错误换脚。",
8:"左脚加载承重；左右臂位置已重画以接09。",
9:"左腿支撑、右腿后收，反向手臂已重画。",
10:"左腿承重，右腿恢复；右空手由前摆向中位回落。",
11:"通过位候选，右腿前送；两手已改为回转中位。",
12:"两轮重绘后左跟抬起、前掌低，左腿蹬离可辨；右腿收起。",
13:"短暂腾空成立，右靴下缘约y885，区别于支撑带933–951；两手反相。",
14:"二次重绘为双脚收起短飞行，双靴下缘约y885；不额外宣称重心顶点。",
15:"实图为右脚初触地（约y936），左腿后收，不能继续叫预接触。",
16:"实图右脚加载约y951，左腿后屈；16→01同一右脚可追踪。"
}
for f,note in phases.items():
 p=ROOT/"runtime/run/N"/f"{f:02d}.png"
 rows.append({"slot":f"run/N/{f:02d}","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"status":"passed","staticAnatomy":"passed","evidence":note,"footOrientation":"当前背向靴跟和抬起的鞋底长轴顺着小腿，未见左右横向外撇；靴边挂饰不当作脚尖。","reviewBasis":"当前原图、audit/feet-run-N-current.jpg及独立只读逐腿复核；audit/root-review-20261003.md末尾更新为准。未把其他角色任何方向当作已通过模板；单帧通过不代替整段动态。","dynamicApproval":False})
out={"reviewedAtUtc":datetime.now(timezone.utc).isoformat(),"reviewMethod":"逐帧原图与更新后16格接触表实际查看；正常/慢速GIF已生成，不等同实播动态验收。","frames":rows,"sequences":[{"sequence":"run/N","status":"needs_review","frameSha256":[x["sha256"] for x in rows],"evidence":"当前01–03右支撑、04右前掌蹬离、05/06短飞行、07左接触、08–11左支撑、12左前掌蹬离、13/14短飞行、15右接触、16右承重接01。N01/12/13/14最新修订已查看，脚长轴无横向外撇，左持弓/右空手反相保持。正常尺寸实播与客户端位移匹配尚未验收。","trialCycleMs":[1200],"defaultTrialCycleMs":1200,"oldBaselineMs":480,"clientTimingConfirmed":False}],"grounding":{"rootPromptTarget":[512,940],"confirmed":False,"contactFrames":[7,15],"loadingAndSupportFrames":[1,2,3,8,9,10,11,16],"takeoffFrames":[4,12],"briefFlightFrames":[5,6,13,14],"precontactFrames":[],"note":"相位以当前实图为据。支撑带约y933–951，蹬离前掌可更低；N透视前后脚屏幕y可不同，提示根点不代表客户端地面已标定。"}}
(ROOT/"review-parts/run-N.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("N review updated without automatic approval.")


from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent
R=O.parents[1]
slots=['attack/E/03','attack/E/05','attack/W/03','attack/W/05','cast/E/09','cast/W/10','run/W/16','run/W/01','hit/W/06','cast/W/16','attack/W/01','attack/W/12']
sources=[]
for slot in slots:
 p=R/'runtime'/f'{slot}.png'
 sources.append({'slot':slot,'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'inspection':'direct original PNG viewed at 1024 canvas'})
uncertainty={'status':'uncertain','groups':['hit/W','cast/W','attack/W','run/W'],'issue':'仅剩跨动作是否需要转枪过渡：实际查看 run16/01、hit06、cast16、attack01/12。run/hit/cast 的可见肩袖—掌腕布局连续，attack 组采用朝左刺的独立布局，组内12→01握持没有交换。跨动作之间没有提供转枪中间帧，不能仅凭枪头变向断言错手。','decision':'没有确认单帧解剖错误；不为缺少跨动作中间证据而盲改所有战斗帧。若客户端直接把不同动作首尾硬接，应另验状态切换；目前不是已确认的错误帧。'}
add={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reason':'Follow-up targeted audit of sustained foot turnout and W cross-action grip, not only sudden sole flips.','sources':sources,'legAxisFindings':[{'slots':['attack/E/03','attack/E/05'],'status':'passed','observation':'最大横向弓步中护胫正面、踝连接、鞋面主轴连续。前膝屈曲与后腿蹬伸在动作平面内。后腿斜向左、鞋尖向右的投影并不代表扭踝：后腿伸展而脚掌仍朝攻击方向是自然弓步。'},{'slots':['attack/W/03','attack/W/05','cast/W/10'],'status':'passed','observation':'前腿弯曲、后腿外展，护胫正面随大腿整体转向，鞋面也随之朝左前；未见小腿正面朝一侧、踝以下却横扭另一侧的断轴。宽站距本身保留。'},{'slots':['cast/E/09'],'status':'passed','observation':'低重心宽站距，两腿分别从髋展开，左侧后足略向镜头，护胫与踝部同向；没有仅鞋头从踝部折成侧向的形态。'}],'crossAction':uncertainty,'result':{'newConcreteFailures':0,'edits':0,'preserveCurrentBattleFrames':True,'interpretation':'髋—膝—踝—鞋头同一运动平面，不等于二维画面中的四点必须成一条直线。'}}
(O/'axis-and-grip-addendum.json').write_text(json.dumps(add,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=O/'audit.json';audit=json.loads(p.read_text(encoding='utf-8'));audit['sequenceUncertainties']=[uncertainty];audit['targetedFollowUp']='full-limb-review-20261004/battle-audit/axis-and-grip-addendum.json';p.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=O/'REVIEW.md';text=p.read_text(encoding='utf-8')
old='跨动作握序标记为 uncertain：hit/cast W 的枪头朝右上，attack W 枪头朝左。宽袖遮住远肩和完整肘线，单帧握持和同动作序列无明确错误，但不能据此宣称跨动作转枪时解剖左右完全确认；交总控结合切换段判读，不据此重画完整战斗组。'
new='补查后将 uncertain 收窄为“跨动作是否需要转枪过渡”，不再仅因枪头改变朝向而怀疑错手。已实际查看 run W16/01、hit W06、cast W16、attack W01/12 原图：run/hit/cast 可见肩袖—掌腕布局连续；attack 组为独立朝左刺的布局，组内12→01握持连续。缺少不同动作之间的转枪中间帧，不能从首尾单独判定解剖错误。没有确认的错手帧，因此不盲改整组。'
assert old in text;text=text.replace(old,new)
text+='\n## 支撑轴线追加复查\n\n按最新要求进一步直接查看 attack E03/E05、W03/W05、cast E09/W10 的最大弓步和支撑展开原图，重点比对髋部出腿、膝盖/护胫正面、踝部连接和鞋面主轴，未发现持续扭踝的明确错位。护胫与鞋面随整条腿一起转，而非小腿向前、仅鞋掌横撇。后腿斜伸且脚尖仍朝攻击方向属于自然弓步；髋—膝—踝—鞋头处在同一运动平面，不要求在二维画面排成直线。追加复查来源SHA与具体判读见 axis-and-grip-addendum.json。明确新增错误0，编辑0，保留战斗68帧。\n'
p.write_text(text,encoding='utf-8')
print('Targeted leg axis and W grip follow-up saved; no confirmed new error; runtime untouched')

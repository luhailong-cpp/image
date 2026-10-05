from pathlib import Path
from datetime import datetime,timezone
import json
O=Path(__file__).resolve().parent
src=json.loads((O/'source-sha.json').read_text(encoding='utf-8')); lookup={x['file'].replace('runtime/','').replace('.png',''):x for x in src}
order=[13,14,15,16,1,2,3,4,5,6,7,8,9,10,11,12]
def item(direction,n,support,confidence,obs):
 slot=f'run/{direction}/{n:02}';return {'slot':slot,'source':lookup[slot],'inferredSupportAnatomicalSide':support,'confidence':confidence,'observation':obs}
E=[]
for n in order:
 if n==13: E.append(item('E',n,'L','high','近侧右腿的大腿与后折小腿盖在落地腿前；远侧左腿落地。'))
 elif n==14:E.append(item('E',n,'R','medium-high','与13落地位置相近，但落地大腿轮廓盖在横向后折的悬空腿前；读为近侧右腿落地，与13及15前后遮挡反转。'))
 elif n in [15,16,1,2,3,4]:E.append(item('E',n,'L','high' if n in [15,16,1,2,3] else 'medium','高抬/前伸的近侧右大腿在前，远侧落地腿从裙下向后延伸；脚掌位置后移不等于换腿。'))
 else:E.append(item('E',n,'R','high' if n in [5,6,7,8,9] else 'medium','落地腿从近侧裙缘接出并居前，另一腿在其后后折或向前摆；由05到12落地靴逐步向后移。'))
W=[]
for n in order:
 if n in [13,14]:W.append(item('W',n,None,'uncertain','前下落地腿和后折悬空小腿均可见，但髋部与两大腿交叠完全被裙摆遮住，没有可靠的前后遮挡线决定解剖左右；不能因脚位在前就贴左/右。'))
 elif n in [15,16,1,2,3]:W.append(item('W',n,'R','high','近侧左大腿和高抬靴明确盖在落地腿前，落地腿读为远侧右腿；16→01只是支撑点后移，归属未换。'))
 elif n==4:W.append(item('W',n,'R','medium','由03相同落地踝向右后连续伸展，近侧摆腿向左前伸；髋隐藏，靠相邻连续性推断。'))
 elif n in [5,6]:W.append(item('W',n,'L','medium','前下落地腿从较近裙缘接出，后折悬空小腿居后，读为左支撑；髋部仍有遮挡。'))
 elif n in [7,8]:W.append(item('W',n,'L','high','落地大腿/胫段处于前景，后折悬空小腿被它和裙摆遮住，读为近侧左腿支撑。'))
 elif n in [9,10,11]:W.append(item('W',n,'R','medium-high','高抬悬空左膝与靴读为前景，落地腿从它后面向右后伸出，读为远侧右腿；与07/08的前后遮挡相反。'))
 else:W.append(item('W',n,'R','medium','沿09–11落地踝轨迹伸向右后，左前自由腿伸出；髋受裙摆遮挡，不能仅本帧单独证明归属。'))
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'Independent read-only phase audit of current run E/W 32 PNGs','basis':'Directly viewed all 32 original PNGs plus fixed body contact sheets in circular order 13..16,01..12. Did not read RUN_CONTACT_PLAN or derive identity from its labels. Near limb inferred from front/back overlap; E near side is anatomical R and W near side is anatomical L.','results':{'E':'八帧分段的总体运动可读为13→04左支撑、05→12右支撑，但14帧遮挡与该归属相反，当前不能判完整8+8通过。','W':'不能证实完整8+8。07/08与09–11的前后遮挡反转，存在08→09提前换支撑腿的视觉读法；13/14受裙摆遮挡无法独立定左右。','notAFourFrameProof':'04→05与12→13是相隔8帧的两个边界。若把01当播放起点，13→04自然显示为末尾4张+开头4张，不能据此声称每4帧换腿。'},'actionableReadabilityProblems':[{'direction':'E','slots':[13,14,15],'status':'not-passed','issue':'14落地腿与悬空腿的近远遮挡反转；不能仅以落地位置接近13而认为同一腿持续支撑。','minimalFocus':'优先复核/修14的髋—大腿连接及前后遮挡，保留其落地点及同位置的独立膝踝变化。'},{'direction':'W','slots':[7,8,9,10,11,12],'status':'not-passed','issue':'08→09落地腿从前景变为后景，高抬腿成为前景，不能凭落地点连续认同一支撑腿。','minimalFocus':'复核09–12前后腿归属，和07/08的近侧左支撑衔接。'},{'direction':'W','slots':[13,14],'status':'uncertain','issue':'裙摆遮住髋和大腿交叠，缺少可见归属证据；不能强行判通过或仅因与05/06轮廓相似就判同一腿。','minimalFocus':'由负责修稿代理在相邻帧链中检查髋腿衔接可读性。'}],'frames':E+W,'edits':0,'runtimeMutated':False}
(O/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 东、西向支撑相位独立复核','', '只读检查当前 runtime/run/E、W 共32张原图，并按13→14→15→16→01…→12看完整圈；没有读取或照抄 RUN_CONTACT_PLAN 的支撑标签。完整源SHA见 source-sha.json，逐帧左右、置信度和像素依据见 audit.json。','', '**04→05、12→13本身不是每4帧换腿的证据**：两个边界相隔8帧。若从01显示，13→04这个8帧段本来就被拆成末尾4张和开头4张。','', '不过当前实图不能整体判8+8通过：','', '- **E/14需复核**：E/13是近侧右腿后折并覆盖远侧落地腿；14反而画成落地大腿覆盖后折腿，读为近侧右支撑；15→04又是右腿在前悬空、左腿落地。主要问题是14的近远遮挡，不能凭脚位近似就认同一支撑腿。05→12的右支撑整体可读。','- **W/08→09存在提前换腿的视觉读法**：07/08的落地大腿和胫段在前，读为近侧左支撑；09–11高抬膝/靴在前、落地腿向右后从后面接出，读为远侧右支撑。12沿该落地踝轨迹继续。需定向复核09–12的髋腿连接和遮挡，不能靠计划标签补足证据。','- **W/13、14保留uncertain**：两条腿髋部和近端大腿都被裙摆遮住，单看它们无法可靠决定解剖左右；不因脚位在左侧或轮廓像另一半圈而强贴左右。15、16、01–03近侧左摆腿覆盖远侧右支撑腿的关系较清楚。','', '这里的“左/右”是从侧身视角与可见前后遮挡推断的角色解剖左右，不是画面左右。对于完全被裙摆遮住的髋，不声称看见骨骼。所有结论只用于定位可读性和相邻归属错误；没有改图、改帧序或写runtime。','', '| 方向 | 顺序 | 独立推断支撑腿 | 置信度 |','|---|---|---|---|']
for direction,rows in [('E',E),('W',W)]:
 for x in rows:lines.append(f'| {direction} | {x["slot"].split("/")[-1]} | {x["inferredSupportAnatomicalSide"] or "uncertain"} | {x["confidence"]} |')
(O/'REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Saved independent phase findings; E14 and W08->09 not passed, W13/14 uncertain')

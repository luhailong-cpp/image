"""Apply the user's exact 16*75ms run timing to current builders, not historical evidence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'tools/build_preview.py';s=p.read_text(encoding='utf-8-sig').replace('跑步（720ms试播）','跑步（1200ms / 圈）').replace('"count": 16, "duration_ms": 45},\n    "hit"','"count": 16, "duration_ms": 75},\n    "hit"').replace('跑步默认720ms/圈试播，正式时长仍待复核','跑步正常1×统一1200ms/圈，16帧各75ms；客户端速度未接入').replace('480/640/720/800ms接地与节奏对比','1200ms正常与慢放接地复核');p.write_text(s,encoding='utf-8')
p=R/'tools/build_delivery.py';s=p.read_text(encoding='utf-8-sig').replace('"NW"],16,45)','"NW"],16,75)')
lines=s.splitlines()
for i,line in enumerate(lines):
 if "out['runTimingReview']=" in line:lines[i]=" out['runTimingReview']={'requestDate':'2026-10-03','selectedNormalCycleMs':1200,'uniformFrameMs':75,'durationsMs':[75]*16,'speedOptions':[1,0.25],'oldFastOptionsRemoved':True,'status':'用户指定正常1×1200ms，16帧均匀75ms；不套分相位权重，客户端未接入','preview':'preview/timing-grounding-20261003/index.html','referenceGroundVerified':False,'clientVerified':False}"
s='\n'.join(lines)+'\n'
s=s.replace('run当前45ms/帧是720ms/圈试播，正式值未选','run正常1×为75ms/帧、1200ms/圈，按用户最新要求已用于素材预览与清单；客户端未接入')
s=s.replace('用户反馈正常步频过快、缺少落地感。run 30ms/帧（480ms/圈）仅作为旧节奏对照；最终循环总时长、逐帧时长仍未选定。新增640/720/800ms均匀试播，720只是比较起点。受击、普攻、施法节奏不随此反馈更改。','用户指定正常跑步每圈1200ms，16帧均匀75ms，精确整除；当前正式选项已移除480/640/720/800ms快档。保留正常、慢放、暂停与逐帧，不在首尾额外停顿。受击、普攻、施法节奏保持原值。')
s=s.replace('本角色新旧节奏比较','本角色1200ms正常与慢放').replace('逐帧来源与试播时长','逐帧来源与当前时长').replace('本机缺客户端不影响素材生成。','2026-10-03末只读确认本机客户端目录现已存在；本任务仍仅写角色私有目录，未接入或运行客户端。')
p.write_text(s,encoding='utf-8')
p=R/'tools/inspect_assets.py';s=p.read_text(encoding='utf-8').replace('"count": 16, "duration_ms": 30}','"count": 16, "duration_ms": 75}');p.write_text(s,encoding='utf-8')
p=R/'tools/build_timing_grounding.py';s=p.read_text(encoding='utf-8');s=s.replace("'oldCycleMs':480,'trialCycleMs':[640,720,800],'selectedFinalCycleMs':None,'defaultTrialMs':720,'durationsFinalMs':None","'normalCycleMs':1200,'slowCycleMs':4800,'selectedNormalCycleMs':1200,'defaultCycleMs':1200,'durationsMs':[75]*16").replace('[480,640,720,800]','[1200,4800]').replace("'status':'试播与接地复核中，未验收'","'status':'正常1×1200ms已采用；手脚接地继续复核'").replace("'finalTiming':None","'normalTiming':1200");p.write_text(s,encoding='utf-8')
p=R/'tools/timing_grounding_template.html';s=p.read_text(encoding='utf-8');s=s.replace('左右使用同一组真实帧，只改变试播时长。720毫秒是比较起点，最终节奏尚未通过；承重姿态与手脚仍须单独检查。','正常1×跑步为1200毫秒/圈，16帧均匀75毫秒；右侧可慢放，手脚与承重仍逐向检查。')
s=s.replace('<label>试播 <select id="cycle"><option value="640">640ms / 圈</option><option value="720" selected>720ms / 圈</option><option value="800">800ms / 圈</option></select></label>','<label>右侧速度 <select id="cycle"><option value="1200" selected>正常 1× · 1200ms</option><option value="4800">慢放 ¼× · 4800ms</option></select></label>')
s=s.replace('旧节奏 · 480ms / 圈','正常 1× · 1200ms / 圈').replace('alt="旧节奏"','alt="正常节奏"').replace('试播 · 720ms / 圈','正常 1× · 1200ms / 圈').replace("' / 15 · 30ms'","' / 15 · 75ms'").replace('at(elapsed,480)','at(elapsed,1200)').replace('16张候选已加载；相位和最终节奏未通过。','16张候选已加载；正常1200ms，手脚接地仍须复核。').replace("'试播 · '+$('cycle').value+'ms / 圈'","($('cycle').value==='1200'?'正常 1×':'慢放 ¼×')+' · '+$('cycle').value+'ms / 圈'")
p.write_text(s,encoding='utf-8')
p=R/'tools/record_oblique_phase_review.py';s=p.read_text(encoding='utf-8').replace('最终循环时长待640/720/800比较','1200ms正常节奏下检查完整首尾与承重');p.write_text(s,encoding='utf-8')
timing={'run':{'frameCount':16,'frameMs':75,'cycleMs':1200,'durationsMs':[75]*16,'slowFactor':4,'slowCycleMs':4800,'oldFastOptionsRemoved':True,'status':'user_selected_offline_default_applied','clientConfirmed':False},'hit':{'frameMs':40,'cycleMs':240},'attack':{'frameMs':30,'cycleMs':360},'cast':{'frameMs':45,'cycleMs':720},'clientIntegration':'not_integrated','referenceCharacter':'09_bamboo_archer_girl, read-only pose comparison; no copied phases/pixels'}
(R/'animation-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('run 16*75=1200ms; combat unchanged; current builders updated')

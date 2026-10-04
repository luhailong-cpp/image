import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
result={'character':'02_fire_talisman_boy','reviewedAt':datetime.now(timezone.utc).isoformat(),'status':'in_progress','cycles_ms':[480,640,720,800],'adopted_cycle_ms':None,'client_validation':'未接入，未完成位移速度及滑步验收','root':{'reference':[512,920],'calibrated':False,'definition':'固定虚拟地面诊断标记，不读取最低alpha点做逐帧贴地。支撑鞋实际地面投影和比例仍需统一复核。'},'display':{'canvas_css_px':160,'client_size_confirmed':False,'large_css_px':384},'directions':{}}
phases=['右脚初触候选','右脚屈膝承重','右脚中支撑，左膝前摆','右前掌蹬离候选','左腿前摆，短暂腾空','左腿前伸腾空','左脚下降','左脚预接触','左脚初触候选','左脚屈膝承重','左脚中支撑，右膝前摆','左前掌蹬离候选','右腿前摆，短暂腾空','右腿前伸腾空','右脚下降','右脚预接触']
weights=[55,70,65,50,25,25,30,40]*2
for d in ['E','SE']:
    frames=[]
    for n in range(1,17):
        p=R/'frames'/'run'/d/f'{n:02}.png'
        frames.append({'frame':n,'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actualPhase':phases[n-1],'phaseConfidence':'medium_requires_continuity_review','trialDurationMs':weights[n-1],'visualStatus':'candidate_not_final_pass'})
    result['directions'][d]={'complete':True,'timing':{'cycleMs':720,'durationsMs':weights,'status':'本角色实图相位试值；非客户端定稿'},'frames':frames,'remaining':['整体比例与虚拟地面校准','正常尺寸及放大下检查首尾衔接','腾空5至8、13至16的足踝下降是否足够连续','局部道具卡数返修后复核']}
for d in ['W','N','S']:
    paths=list((R/'work'/('run-'+d)).glob('*grounding*.json'))
    if paths:
        p=sorted(paths,key=lambda x:x.stat().st_mtime)[-1]
        result['directions'][d]={'reviewReference':p.relative_to(R).as_posix(),'status':'由逐图审阅表读取，动态未定稿'}
(R/'reviews'/'run-grounding-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({'reviewFrames':32,'trialMs':sum(weights)})

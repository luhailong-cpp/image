import json,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
r=Path(__file__).resolve().parents[1]
inv=json.loads((r/'inventory-hit.json').read_text(encoding='utf-8-sig'))
phases=[
('左脚初接触候选','近左腿前伸、前鞋跟较低而前掌略抬；远右腿后收'),
('左脚屈膝承重','近左腿膝下压、鞋底平，远右脚抬起'),
('左脚单支撑，右腿过腿','近左腿在身体下支撑，远右膝在viewer左抬过；鞋头沿SW'),
('左脚晚支撑，右腿前摆','a2真实重画远右腿向前；近左后鞋前掌朝下，前远右鞋悬空'),
('左脚蹬离，右腿前摆','a2后近左腿伸展、前掌向下蹬离；远右鞋前伸亮出鞋底'),
('短飞行，右前左后','近左后踝重建后，后鞋跟在右上鞋尖左下；前远右鞋也朝SW'),
('右腿下降','远右前腿在下落，后近左腿收起，后鞋已从右下外转改为前掌左下'),
('右脚触地前','远右前鞋降低、仍见窄底；近左后鞋脚跟在右上'),
('右脚初接触候选','前远右鞋已近于平底，后近左腿收；初接触与10压缩对比待实播'),
('右脚屈膝承重','前远右鞋平底，膝位于身下，后近左脚悬空'),
('右脚单支撑，左腿过腿','a3真实重画：近左大腿从viewer右髋向前抬膝，前景鞋悬空；远右腿在骨盆下单支撑。主代理已独立实看局部修正通过。'),
('右脚晚支撑，左腿前摆','a2近左大腿从viewer右髋向左前穿过，远右后鞋前掌下指支撑'),
('右脚蹬离，左腿前摆','a2远右腿在后伸展，前掌下指；近左前鞋抬起可见底'),
('短飞行，左前右后','近左腿前伸、远右后腿收起；后踝联动修正成鞋头左下'),
('左腿下降','近左前鞋向下、远右鞋后收；a3修后踝、a4清理左边孤立杂片'),
('左脚触地前','近左前鞋下降准备回到01，远右后鞋跟在右上脚尖向左下')
]
dur=[50,75,65,45,40,25,25,35,50,75,65,45,40,25,25,35]
j={'schema':1,'action':'run','direction':'SW','updatedAt':datetime.datetime.now(ZoneInfo('America/New_York')).isoformat(),'reviewMethod':'逐帧实际查看生成结果和整画布联系表；未将提示词当验收；最终正常/慢速播放由主代理完成','userCriterion':'没有整套已通过方向；逐图判断真实鞋跟到鞋尖轴向，只改外转，不仅缩腿距。未附07参考图。','root':{'declared':[512,920],'registration':'仅整1254画布统一1024导出，无bbox裁切缩放及最低脚对齐。局部编辑造成的意外放大另以AI纯相机修订，未与鞋向目标混在同次调用。'},'timing':{'status':'本角色实画相位的候选时长，非正式manifest/客户端设置','cycle_ms':720,'durations_ms':dur,'compare_cycles_ms':[480,640,720,800],'note':'与S周期相同基于本角色交替支撑，接触承重更长、短飞更短；未复制07参数。'},'frames':[],'unresolved':['主代理需正常与慢速实播确认头身物理尺度/根点起伏连续，特别相机修订后的05→06→07、08→09→10、13→14→15→16','03/11为两次过腿相位，但近远髋遮挡仍需在动态中持续追踪左右腿，不能仅依据道具方向判腿身份','01/09接触到02/10承重的膝踝压缩须实播确认；静态支点不等于落地感通过','本机无客户端，位移同步/滑步和游戏真实尺寸未接入验收'],'clientStatus':'未接入，本机无客户端'}
for f in sorted((f for f in inv['frames'] if f['action']=='run' and f['direction']=='SW'),key=lambda f:f['frame']):
    n=f['frame'];row=dict(f);row.update(actual_phase=phases[n-1][0],contact_evidence=phases[n-1][1],toe_axis_review='鞋跟与鞋尖方向已实看；当前以左下前进方向为主，未见此前后鞋明显朝右下反向外转',review_status='静态候选；连续性、尺度、接地感待主代理实播',suggested_duration_ms=dur[n-1])
    j['frames'].append(row)
p=r/'work/run-SW/run-SW-grounding-review-20261003.json'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(p),'count':len(j['frames']),'cycle_ms':sum(dur)},ensure_ascii=False))


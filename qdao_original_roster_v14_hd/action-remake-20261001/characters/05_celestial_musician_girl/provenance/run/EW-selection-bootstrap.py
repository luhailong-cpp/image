from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
old=json.loads((r/'selected-files.json').read_text(encoding='utf-8-sig'))['files']
ew=[]
wver={1:4,10:1,11:2,12:2}
for d in ['E','W']:
 for n in range(1,17):
  prior=next((x for x in old if x['action']=='run' and x['direction']==d and x['frame']==n),None)
  if d=='E':
   p=prior['file'];g=prior['generationRecord']
  else:
   v=wver.get(n,1);p=f'staging/run/W/{n:02d}-v{v}.native.png';g=f'provenance/run/W{n:02d}-v{v}.generation.json'
  note='已看整段静态连图，独立姿态候选；动态与统一根点校准待审。'
  status='candidate'
  if d=='W' and n==10:status='needs_correction';note='缓冲支撑鞋底y约1179，较W09/W11承重点1200偏高约21px；v2/v3仍未解决，拒用更高版本。'
  if d=='W' and n==12:note='v2原生AI修复v1右缘alpha195截带；腿姿态保留；待动态与根点。'
  if d=='W' and n in (1,2,3,9,11):note+=' 原生承重鞋底约y1200/1254，不能将提示词92%地面当作已配准。'
  if d=='W' and n==8:status='needs_correction';note='计划预接触，但鞋底已达y1208，比W09 y1205更低；需要修正接触次序，不能最低脚逐帧对齐。'
  if d=='E' and n in (7,8,16):status='needs_correction';note='计划下降/预接触，但原生鞋底低于E01/E09接触地面约8–12px；需要校正脚踝/腿姿态或核实统一根点，不逐帧抬整图。'
  if d=='E' and n in (3,11):note+=' 已见前摆腿与支撑腿交叠；仍需正常尺寸动态确认换腿清楚。'
  ew.append(dict(action='run',direction=d,frame=n,file=p,generationRecord=g,reviewStatus=status,notes=note))
(r/'provenance/run/selection-EW.json').write_text(json.dumps(ew,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
attack=[]
for n,v in [(1,2),(2,3),(3,1)]:
 p=f'staging/attack/W-{n:02d}-v{v}.png';g=p+'.generation.json'
 attack.append(dict(action='attack',direction='W',frame=n,file=p,generationRecord=g,reviewStatus='candidate',notes='已逐图查看；近左袖跨琴至上端、远右袖从琴后露出，序列/根点待审。'))
(r/'provenance/attack/selection-W.json').write_text(json.dumps(attack,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT/'work').glob('run_E_*.png.generation.json'):
 r=json.loads(p.read_text(encoding='utf-8'))
 changed=False
 for ref in r.get('references',[]):
  if '07_moon_shadow_assassin_girl' in ref['path']:
   ref['role']='实际查看后的局部姿态比较；仅参考脚掌/膝踝同运动平面，不能作为07整套或该方向已确认正确的证据'
   changed=True
 if changed:
  r['laterUserSteering']={'date':'2026-10-03','note':'用户撤回月影少女整套正确及垂直方向正确的判断。逐帧独立复核外撇，已正确者保留；07只有局部对照价值。原始已提交prompt保留原样供审计。'}
  r['submittedParameters']['prompt']=(ROOT/r['prompt']).read_text(encoding='utf-8-sig')
  p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated actual source roles and later steering; original submitted prompt preserved')

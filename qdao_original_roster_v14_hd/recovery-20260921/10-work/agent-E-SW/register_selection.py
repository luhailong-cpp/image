from pathlib import Path
import json
from datetime import datetime,timezone
b=Path(__file__).resolve().parent
p=b/'selection.json'
s=json.loads(p.read_text(encoding='utf-8'))
overrides={'E04':690,'E05':690,'E13':720,'E14':720,'E-idle':650,'SW05':585,'SW13':585,'SW-idle':575}
for k,v in s.items():
  d='SW' if k.startswith('SW') else 'E'
  v['nativeRootX']=overrides.get(k,600 if d=='SW' else 735)
  v['nativeRootY']=1200 if d=='SW' else 1185
  v['rootReview']='2026-09-28 manually viewed full native1254 sprite and all-frame light/dark sheets. X is pelvis projection, Y is virtual ground plane shared within direction; airborne feet and gun tassels excluded. Initial registration for final dynamic review.'
  v['registrationEvidence']=('Anatomical pelvis horizontally displaced in native generation layout; per-frame X correction only, not new pose synthesis.' if k in overrides else 'Consistent native body placement in this directional series; retain intrinsic leg movement and perspective at a fixed virtual ground plane.')
  if k=='E06':
    v['boundaryReview']={'acceptedException':True,'maximumAlpha':65,'pixelCountAbove8':3,'reason':'At4x light composite both metal edges converge into complete tip; no flattened/cut contour. Boundary antialias extension only.','evidence':'10-work/agent-E-SW/qa-current/E06-tip-detail.jpg'}
p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:[v['nativeRootX'],v['nativeRootY']] for k,v in s.items()},ensure_ascii=False))

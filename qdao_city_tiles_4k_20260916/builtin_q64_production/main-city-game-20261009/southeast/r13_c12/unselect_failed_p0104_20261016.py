from pathlib import Path
import json
T=Path(__file__).resolve().parent
p=T/'active-native-map.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
assert d['p01_04']=='p01_04_v20261016T142051_a5eefa89'
snap=T/'review/quick-p01_04_v20261016T142051_a5eefa89/active-before-unselect.json'
with snap.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
del d['p01_04'];p.write_text(json.dumps(d,indent=2),encoding='utf-8')
p=T/'progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'))
d.update(activeNativeCount=1,status='p01_04_failed_initial_pending_one_retry',formalAccepted=False)
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
print('Retained native; only failed p01_04 selection removed.')


from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3]
G=R/'qdao_original_roster_v14_hd/recovery-20260921/05-generation'
P=G.parent/'05-delivery-preview'
if (P/'final/manifest.json').exists():
 raise SystemExit('05 is finalized. This historical staging assembler is retired; validate 05-delivery-preview/final/manifest.json instead.')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(P/'selected-overrides.json')
for name in ['NW-selection.json','SW-selection.json','W-selection.json','SE-back-selection.json']:
 for r in read(G/name)['rows']:
  p=Path(r['output'])
  assert p.exists() and sha(p)==r['sha256'],p
  s['overrides'][r['slot']]={'path':str(p),'sha256':sha(p),'selected_revision':p.parents[5].name,'visual_status':'static_reviewed_pending_dynamic'}
for n in [1,2,3,4,5,6,7,8,9,13]:
 v=2 if n in [4,5,8,9,13] else 1
 d=f'SE{n:02d}-single-v{v}'
 p=G/d/'staging/candidate/05_celestial_musician_girl/walk/SE'/f'{n:02d}.png'
 assert p.exists(),p
 s['overrides'][f'walk/SE/{n:02d}.png']={'path':str(p),'sha256':sha(p),'selected_revision':d,'visual_status':'static_reviewed_pending_dynamic'}
s['status']='128_walk_8_idle_selected_pending_full_review'
s['known_rework_slots']=[]
s['review_notes']={}
(P/'selected-overrides.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Selected',len(s['overrides']),'overrides')

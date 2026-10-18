from pathlib import Path
import json,datetime
T=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r13_c12")
a=json.loads((T/'active-native-map.json').read_text(encoding='utf-8-sig'))
v='p02_04_v20261016T133928_b0df564e'; assert a=={'p02_04':v}
d={'version':v,'nativeSha256':'35f9b27a24e12a9b1d1015d1ea0c4eaa8512a8bec2e47529128af7e0a1f96676','reviewStatus':'root_rereviewed_native_and_actual_layout','rightEdgeLocalQA':'previous local continuity evidence remains valid for that edge only','layoutStatus':'failed; added decorative blue inset strip crosses left y500 while approved cream ground boundary only enters near left y950','formalAccepted':False,'decision':'retain native and earlier QA; supersede overall propagation readiness; unselect and correct layout before continuation','activeBefore':a}
p=T/'review'/'seed-layout-correction-20261016.json'
with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
(T/'active-native-map.json').write_text('{}',encoding='utf-8')
p=T/'progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(activeNativeCount=0,status='initial_seed_layout_failed_pending_corrected_seed',formalAccepted=False);p.write_text(json.dumps(d,indent=2),encoding='utf-8')


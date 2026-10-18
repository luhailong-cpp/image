import json
from pathlib import Path
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r16_c12");p=t/"local-content.json";d=json.loads(p.read_text(encoding="utf-8"))
for row in range(1,5):
 d[f"p{row:02d}_02"]=d[f"p{row:02d}_03"]+" In the newly painted area use sparse soft irregular stone grain, avoiding amplification of repeated lattice/cell patterns. A groove entering from an anchor must continue until the next true perpendicular joint, never end within a slab."
d["p04_02"]+=" The wall-foot foliage is mostly lower-left in this crop, with quieter exposed dark stone towards lower-right, following the guide; maintain the RIGHT native leaves where present. Dark foundation is AXIS-ALIGNED rectangular slabs, never diagonal tiles or diamond paving. Keep all horizontal ledges at exact anchor heights."
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")

import json
from pathlib import Path
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r16_c12")
p=t/"local-content.json"
d=json.loads(p.read_text(encoding="utf-8"))
for row in range(1,5):
 d[f"p{row:02d}_03"]=d[f"p{row:02d}_04"]+" The RIGHT anchor is the saved adjacent native patch; preserve its exact joints and continue them across the new leftward wall section. Keep unobstructed wall in rows 1-3. Slab joints are thin, regular, logically connected; no blind ends. Match fine mineral texture without amplifying pattern contrast."
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")

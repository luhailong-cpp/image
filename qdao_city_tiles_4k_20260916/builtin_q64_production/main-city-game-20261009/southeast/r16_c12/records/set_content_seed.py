import json
from pathlib import Path
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r16_c12")
p=t/"local-content.json"
d=json.loads(p.read_text(encoding="utf-8-sig"))
d["p02_04"]="Tight front-facing crop of a giant pale warm-grey limestone wall, NOT ground paving. Broad quiet rectangular wall slabs only, rounded hand-painted bevels and restrained mineral mottling. The RIGHT native strip governs actual colors, slab scale and exact mortar endpoints; coarse guide joint positions are only approximate. Continue its thin horizontal joints LEFTWARD across the full repaint at the identical y positions visible in that strip (near target y145 and y965), with seamless tone and width. Keep broad slabs broad, stagger a few vertical joints naturally; no new pillars, steps, framing, ornaments, vegetation or objects. Do not turn the anchor/new paint boundary at x1139 into a vertical mortar line."
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")

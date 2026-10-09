from pathlib import Path
import json
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c04-v1")
r=json.loads((D/"request.json").read_text(encoding="utf-8"));r["selectedFinalDirectory"]="final-v2";(D/"request.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
(D/"qa-accepted.txt").write_text("Whole native 1254 output and final bottom strip viewed at original scale. Canonical cropped planter base, right ivory rail, lower-right native foliage, clean warm paving retained. Bottom foliage composition uses original known pixels to avoid softened duplicate leaves. Stone joints and foliage join continuously; no warp or tone correction, no new fractures. Adjacent right halo beyond tile boundary remains uncommitted. Actual model/quality unknown.",encoding="utf-8")


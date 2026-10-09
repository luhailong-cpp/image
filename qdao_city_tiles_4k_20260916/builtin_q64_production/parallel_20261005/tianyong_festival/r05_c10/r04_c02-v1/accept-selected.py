from pathlib import Path
import json
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c02-v1")
r=json.loads((D/'request.json').read_text(encoding='utf-8'));r['selectedFinalDirectory']='final-v3';(D/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(D/'qa-accepted.txt').write_text("Whole native1254 joined, full right strip and selected bottom native strip reviewed. Correct canonical left bush, narrow ivory wall, tan planter and paving. Two reference-composition transplants rejected and never used. Final native coordinates align at bottom and right. Leaf ownership switches in flat tan gap y1080..1098 to retain exact lower known leaves without ghost contours. No resizing, warp or recoloring. Actual model/quality unknown.",encoding='utf-8')


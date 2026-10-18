from pathlib import Path
import json,hashlib
W=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r02_c05')
p=W/'receipts/r02_c05_s02_s01_v02.request.json';q=json.loads(p.read_text());q['promptSHA256']=hashlib.sha256(Path(q['promptFile']).read_bytes()).hexdigest();p.write_text(json.dumps(q,indent=2))
src=(W/'production-v5.py').read_text();src=src.replace("def name(r,c):return ", "def name(r,c):return 'r02_c05_s02_s01_v02' if (r,c)==(2,1) else ")
(W/'production-v6.py').write_text(src)


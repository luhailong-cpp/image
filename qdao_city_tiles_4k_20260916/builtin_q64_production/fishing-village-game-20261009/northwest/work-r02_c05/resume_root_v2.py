from pathlib import Path
import json,hashlib
W=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r02_c05')
p=W/'receipts/r02_c05_s02_s04_v02.request.json';q=json.loads(p.read_text());q['promptSHA256']=hashlib.sha256(Path(q['promptFile']).read_bytes()).hexdigest();p.write_text(json.dumps(q,indent=2))
s=(W/'production-v6.py').read_text().replace("def name(r,c):return ","def name(r,c):return 'r02_c05_s02_s04_v02' if (r,c)==(2,4) else ")
(W/'production-v7.py').write_text(s)


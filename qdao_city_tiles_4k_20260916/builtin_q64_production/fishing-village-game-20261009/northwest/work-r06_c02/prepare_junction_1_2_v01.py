from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest'); W=B/'work-r06_c02';src=W/'base-v2/r06_c02.candidate.png';p=W/'guides/r06_c02_junction_1_2_v01.authoritative.png'
assert not p.exists()
Image.open(src).crop((1421,397,2675,1651)).save(p)
Path(str(p)+'.derivation.json').write_text(json.dumps({'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'crop':[1421,397,2675,1651],'resample':False}),encoding='utf-8')

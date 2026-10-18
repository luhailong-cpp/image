from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r06_c02'
src=W/'joint-v2/r06_c02.candidate.png';old=W/'base-v2/extended.png'
im=Image.open(old);im.paste(Image.open(src),(115,115))
p=W/'guides/r06_c02_roof_top_v01.authoritative.png';assert not p.exists()
im.crop((1536,0,2790,1254)).save(p)
Path(str(p)+'.derivation.json').write_text(json.dumps({'coreSource':str(src),'coreSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'haloSource':str(old),'crop':[1536,0,2790,1254],'resample':False}),encoding='utf-8')

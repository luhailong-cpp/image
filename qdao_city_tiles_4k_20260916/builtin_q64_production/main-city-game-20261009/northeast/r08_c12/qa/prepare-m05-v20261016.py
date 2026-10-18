from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northeast/r08_c12')
base=p/'qa/core-baseline/f7529838f3e52b886085/r08_c12-core-baseline.candidate.png'
q=p/'qa/repair-m05-20261016';q.mkdir(exist_ok=True)
out=q/'m05-input-v1.png';assert not out.exists()
Image.open(base).crop((397,397,1651,1651)).save(out)
print(str(out))


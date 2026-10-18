import sys,json,hashlib
sys.dont_write_bytecode=True
from PIL import Image
from pathlib import Path
q=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')/'qa';p=q/'repair-r08c04-1016-v3-b2-after-1254.png';assert not p.exists();Image.open(q/'repair-r08c04-1016-v3-candidate-4096.png').crop([2445,397,3699,1651]).save(p)


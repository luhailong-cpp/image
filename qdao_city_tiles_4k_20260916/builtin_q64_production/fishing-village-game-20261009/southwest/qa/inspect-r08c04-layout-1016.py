import sys,json
from pathlib import Path
from PIL import Image
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest')
contract=json.loads((z.parent/'production-contract.json').read_text(encoding='utf-8-sig'))
im=Image.open(contract['layoutReference'])
b=[12288,28672,16384,32768];scale=1254/57344
p=z/'qa/r08c04-layout-inspection-only-1016.png';assert not p.exists()
im.transform((1024,1024),Image.Transform.EXTENT,[v*scale for v in b],resample=Image.Resampling.NEAREST).save(p)


from pathlib import Path
from PIL import Image, ImageDraw
import json
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast')
m=json.loads((z/'qa/r03_c09-native-v1-20261016-layout-authority-only.png.derivation.json').read_text())
im=Image.open(m['source']).convert('RGB')
im.transform((1254,1254),Image.Transform.EXTENT,tuple(m['sourceBox']),Image.Resampling.BICUBIC).save(z/'qa/r03_c09-layout-authority-1254-only.png')
t=Image.open(z/'tiles/r03_c09-native-v1-20261016.png').convert('RGB')
for name,box in [('upper',(300,0,1900,1254)),('middle',(800,1000,2400,2600)),('tree',(1400,1500,3200,3900))]:
 t.crop(box).save(z/'qa'/f'r03_c09-layout-restart-{name}-100pct.png')


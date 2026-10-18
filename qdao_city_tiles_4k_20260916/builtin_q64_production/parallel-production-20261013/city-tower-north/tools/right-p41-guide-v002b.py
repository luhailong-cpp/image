from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');T=B/'versions/right-r04c14-p41-guide-v002/r04_c14/guides'
im=Image.open(T/'p41-REPAIR-INPUT-only.png').convert('RGB')
for p,v,box,xy in [('p42','v003',(115,115,230,1139),(1139,115)),('p32','v001',(115,1024,230,1139),(1139,0))]:
 im.paste(Image.open(B/f'versions/right-r04c14-{p}-native-{v}/r04_c14/native/{p}.png').convert('RGB').crop(box),xy)
im.save(T/'p41-REPAIR-INPUT-v002-only.png')


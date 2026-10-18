from PIL import Image
from pathlib import Path
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north')
s=Image.open(B/'versions/right-r04c14-p24-native-v002/r04_c14/native/p24.png').convert('RGB')
g=Image.open(B/'versions/right-r04c14-p24-guide-v003/r04_c14/guides/p24-GUIDE-only.png').convert('RGB')
for box in [(0,0,1254,115),(0,1139,1254,1254),(0,115,115,1139)]:s.paste(g.crop(box),box[:2])
p=B/'versions/right-r04c14-p24-guide-v003/r04_c14/guides/p24-REPAIR-INPUT-only.png'
s.save(p)


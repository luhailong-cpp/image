from pathlib import Path
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');Q=B/'qa';s=Image.open(B/'versions/right-r04c14-p31-native-v001/r04_c14/native/p31.png').convert('RGB')
for v in ['v004','v005']:
 t=Image.open(B/f'versions/right-r04c14-p21-native-{v}/r04_c14/native/p21.png').convert('RGB');o=Image.new('RGB',(1024,384));o.paste(t.crop((115,947,1139,1139)),(0,0));o.paste(s.crop((115,115,1139,307)),(0,192));o.save(Q/f'right-r04c14-p21-{v}-south-QA.png')


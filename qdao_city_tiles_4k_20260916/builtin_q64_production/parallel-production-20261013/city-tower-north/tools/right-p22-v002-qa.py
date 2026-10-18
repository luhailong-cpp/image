from pathlib import Path
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');Q=B/'qa'
def im(p,v):return Image.open(B/f'versions/right-r04c14-{p}-native-{v}/r04_c14/native/{p}.png').convert('RGB')
t=im('p22','v002')
for tag,a,c in [('east',t,im('p23','v003')),('west',im('p21','v002'),t)]:
 o=Image.new('RGB',(384,1024));o.paste(a.crop((947,115,1139,1139)),(0,0));o.paste(c.crop((115,115,307,1139)),(192,0));o.save(Q/f'right-r04c14-p22-v002-{tag}-QA.png')
for tag,a,c in [('north',im('p12','v002'),t),('south',t,im('p32','v001'))]:
 o=Image.new('RGB',(1024,384));o.paste(a.crop((115,947,1139,1139)),(0,0));o.paste(c.crop((115,115,1139,307)),(0,192));o.save(Q/f'right-r04c14-p22-v002-{tag}-QA.png')


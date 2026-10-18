from pathlib import Path
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');Q=B/'qa'
def im(p,v):return Image.open(B/f'versions/right-r04c14-{p}-native-{v}/r04_c14/native/{p}.png').convert('RGB')
t=im('p41','v002');w=Image.open(B/'versions/root-repair-v004/r04_c13/native/p44.png').convert('RGB')
for tag,a,c in [('east',t,im('p42','v003')),('west',w,t)]:
 o=Image.new('RGB',(384,1024));o.paste(a.crop((947,115,1139,1139)),(0,0));o.paste(c.crop((115,115,307,1139)),(192,0));o.save(Q/f'right-r04c14-p41-v002-{tag}-QA.png')
a=im('p31','v001');o=Image.new('RGB',(1024,384));o.paste(a.crop((115,947,1139,1139)),(0,0));o.paste(t.crop((115,115,1139,307)),(0,192));o.save(Q/'right-r04c14-p41-v002-north-QA.png')
s=Image.open(B.parents[1]/'main-city-game-20261009/northeast/r05_c14/candidates/r05_c14.candidate.png').convert('RGB');o=Image.new('RGB',(1024,384));o.paste(t.crop((115,947,1139,1139)),(0,0));o.paste(s.crop((0,0,1024,192)),(0,192));o.save(Q/'right-r04c14-p41-v002-south-QA.png')


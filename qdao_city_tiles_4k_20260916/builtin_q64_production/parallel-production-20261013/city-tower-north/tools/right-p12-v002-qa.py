from pathlib import Path
from PIL import Image
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');q=B/'qa'
def op(p,v='v001'):return Image.open(B/f'versions/right-r04c14-{p}-native-{v}/r04_c14/native/{p}.png').convert('RGB')
t=op('p12','v002')
for tag,a,c in [('east',t,op('p13')),('west',op('p11'),t)]:
 out=Image.new('RGB',(384,1024));out.paste(a.crop((947,115,1139,1139)),(0,0));out.paste(c.crop((115,115,307,1139)),(192,0));out.save(q/f'right-r04c14-p12-v002-{tag}-QA.png')
out=Image.new('RGB',(1024,384));out.paste(t.crop((115,947,1139,1139)),(0,0));out.paste(op('p22').crop((115,115,1139,307)),(0,192));out.save(q/'right-r04c14-p12-v002-south-QA.png')
n=Image.open(B/'versions/root-r03c14-p42-native-v001/r03_c14/native/p42.png').convert('RGB')
out=Image.new('RGB',(1024,384));out.paste(n.crop((115,947,1139,1139)),(0,0));out.paste(t.crop((115,115,1139,307)),(0,192));out.save(q/'right-r04c14-p12-v002-north-QA.png')


from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r10_c12');D=R/'repairs';D.mkdir(exist_ok=True);Q=D/'qa-initial';Q.mkdir(exist_ok=True)
a=Image.new('RGB',(4096,2048))
for r in [1,2]:
 for c in [1,2,3,4]:
  p=R/'native'/f'p{r}{c}.png';im=Image.open(p);im.load();a.paste(im.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
for x in [1024,2048,3072]:
 out=Image.new('RGB',(512,1048),'#303030');dr=ImageDraw.Draw(out)
 for k in [0,1]:out.paste(a.crop((x-128,k*1024,x+128,k*1024+1024)),(k*256,24));dr.text((k*256+2,2),f'x{x} row{k+1} NATIVE',fill='white')
 out.save(Q/f'x{x}-top2048-native.png')
out=Image.new('RGB',(1024,1120),'#303030');dr=ImageDraw.Draw(out)
for k in range(4):out.paste(a.crop((k*1024,896,k*1024+1024,1152)),(0,k*280+24));dr.text((2,k*280+2),f'y1024 col{k+1} NATIVE',fill='white')
out.save(Q/'y1024-full-native.png')

from pathlib import Path
from PIL import Image
import numpy as np,json
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016');T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04')
box=(870,1090,1030,1254)
for name in ['edit-target','native','roi-trial01','selection-mask-trial01']:
 Image.open(D/(name+'.png')).crop(box).save(D/(name+'-red-hardware-check.png'))
mask=np.array(Image.open(D/'selection-mask-trial01.png'))
print('Selected pixels in hardware vicinity',int((mask[1090:1254,870:1030]==255).sum()))
a=np.array(Image.open(D/'edit-target.png').convert('RGB'));s=np.array(Image.open(D/'native.png').convert('RGB'));o=np.array(Image.open(D/'roi-trial01.png').convert('RGB'))
print('Target and trial hardware equal',np.array_equal(a[1090:1254,870:1030],o[1090:1254,870:1030]))
print('Raw red arc RGB pixels',int(((s[1130:1145,920:970,0]>s[1130:1145,920:970,1]*1.5)&(s[1130:1145,920:970,0]>120)).sum()))
p=T/'native/s03_02_native01.png'
# same world coordinates: frame origin (397,909), lower source origin (909,1933).
# frame box x870:1030 y1090:1254 -> tile x1267:1427 y1999:2163 -> native x358:518 y66:230.
Image.open(p).crop((358,66,518,230)).save(D/'lower-source-same-world-hardware-check.png')


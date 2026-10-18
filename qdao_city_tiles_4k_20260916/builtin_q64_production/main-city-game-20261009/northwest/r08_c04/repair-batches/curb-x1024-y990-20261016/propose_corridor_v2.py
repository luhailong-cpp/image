from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/curb-x1024-y990-20261016')
base=Image.open(D/'edit-target.png').convert('RGB');raw=Image.open(D/'native.png').convert('RGB')
poly=[(0,850),(1253,210),(1253,365),(0,1020)]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255)
trial=base.copy();trial.paste(raw,(0,0),mask)
mask.save(D/'selection-mask-v2.png');trial.save(D/'roi-trial-v2.png')
boxes={'left':[0,780,260,1120],'right':[1030,160,1254,450],'mid-upper':[400,450,900,730],'mid-lower':[400,600,900,880],'full-context':[0,0,1254,1254]}
for name,box in boxes.items():trial.crop(box).save(D/('v2-'+name+'.png'))
print({'selectedPixelCount':int((np.array(mask)==255).sum())})


from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
Q=P/'combat-qa'
rows=[]
for label,p in [('07 original',ROOT/'runtime/attack/E/07.png'),('08 original',ROOT/'runtime/attack/E/08.png'),('08 v2 proposed',ROOT/'generation/limbs-20261004/combat/attack-E-08-v2.png'),('09 original',ROOT/'runtime/attack/E/09.png')]:
 im=Image.open(p).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
 cell=Image.new('RGB',(512,532),(237,233,216));cell.paste(im.resize((512,512),Image.Resampling.LANCZOS),(0,20),im.resize((512,512),Image.Resampling.LANCZOS));ImageDraw.Draw(cell).text((6,4),label,(10,40,35));rows.append(cell)
board=Image.new('RGB',(2048,532),(237,233,216))
for n,im in enumerate(rows):board.paste(im,(512*n,0))
board.save(Q/'attack-E-07-09-final-comparison.jpg',quality=95)
before=Image.open(ROOT/'runtime/attack/E/08.png').convert('RGBA')
after=Image.open(ROOT/'generation/limbs-20261004/combat/attack-E-08-v2.png').convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
metrics={}
for label,box in [('head',(0,0,1024,465)),('lowerBody',(0,760,1024,1024)),('cauldron',(670,415,890,650))]:
 a=np.array(before.crop(box));b=np.array(after.crop(box));m=a[:,:,3]>100;n=b[:,:,3]>100
 metrics[label]={'alphaIoU':float((m&n).sum()/(m|n).sum()),'meanRGBAbsoluteDifferenceOnMutualAlpha':float(np.abs(a[:,:,:3].astype(float)-b[:,:,:3])[m&n].mean())}
(Q/'attack-E-08-registration.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics))

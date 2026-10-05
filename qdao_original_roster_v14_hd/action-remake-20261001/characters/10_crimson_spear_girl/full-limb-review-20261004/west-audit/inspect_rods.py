from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
r=Path(__file__).resolve().parents[2];p=r/'full-limb-review-20261004/run-NW/09-v4/native.png'
im=Image.open(p);a=np.array(im);o=Image.new('RGB',(1000,700),(234,233,224));d=ImageDraw.Draw(o)
for i,box in enumerate([(340,470,455,625),(610,920,730,1050)]):
    tile=im.crop(box).resize((460,620 if i==0 else 520),Image.Resampling.NEAREST);o.paste(tile,(i*500,30),tile);d.text((i*500+5,5),str(box),fill=(0,0,0))
o.save(r/'full-limb-review-20261004/west-audit/NW09-v4-rod-crops.jpg',quality=98)
for y,x1,x2 in [(505,360,410),(550,395,440),(945,635,690),(960,645,700)]:
    row=a[y,x1:x2];mask=(row[:,3]>128)&(row[:,:3].max(axis=1)<110)
    xs=np.where(mask)[0]+x1
    print(y,xs.tolist())

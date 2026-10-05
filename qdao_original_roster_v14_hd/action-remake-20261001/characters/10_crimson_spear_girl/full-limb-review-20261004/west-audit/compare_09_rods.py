from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
r=Path(__file__).resolve().parents[2];o=Image.new('RGB',(2200,1500),(234,233,224));d=ImageDraw.Draw(o)
for j,v in enumerate((1,2,3,4)):
    im=Image.open(r/f'full-limb-review-20261004/run-NW/09-v{v}/native.png').convert('RGBA');a=np.array(im)
    # Independent fixed crops expose the actual black rod, not gold or palm centers.
    crop=im.crop((330,450,900,1230)).resize((550,750),Image.Resampling.LANCZOS)
    o.paste(crop,(j*550,40),crop);d.text((j*550+10,10),f'09-v{v}',fill=(0,0,0))
    top=im.crop((345,480,440,580)).resize((380,400),Image.Resampling.NEAREST);o.paste(top,(j*550,800),top)
    for y,lo,hi in [(505,355,408),(535,378,425),(550,392,438),(1000,700,800),(1020,700,825),(950,620,700),(960,630,710)]:
        row=a[y,lo:hi];mask=(row[:,3]>128)&(row[:,:3].max(axis=1)<110)
        x=np.where(mask)[0]+lo;print(v,y,x.tolist())
o.save(r/'full-limb-review-20261004/west-audit/NW09-four-rod-candidates.jpg',quality=98)

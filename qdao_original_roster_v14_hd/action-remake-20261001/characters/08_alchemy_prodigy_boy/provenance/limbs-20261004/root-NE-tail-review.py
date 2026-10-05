"""Temporary comparison sheet only; never an asset export or pose transform."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
items=[('NE12 retained','runtime/run/NE/12.png'),
       ('NE13 v2','generation/limbs-20261004/feet-northeast/NE-13-v2.png'),
       ('NE14 v4','generation/limbs-20261004/foot-ne14/14-v4.png'),
       ('NE15 v2','generation/limbs-20261004/foot-ne15/NE15-v2.png'),
       ('NE16 retained','runtime/run/NE/16.png'),('NE01 retained','runtime/run/NE/01.png')]
sheet=Image.new('RGB',(1920,550),'#efe9d9')
draw=ImageDraw.Draw(sheet)
for i,(label,file) in enumerate(items):
    im=Image.open(ROOT/file).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
    full=im.resize((320,320),Image.Resampling.LANCZOS)
    leg=im.crop((320,650,900,1024)).resize((310,200),Image.Resampling.LANCZOS)
    x=i*320
    sheet.paste(full,(x,20),full)
    sheet.paste(leg,(x+5,345),leg)
    draw.text((x+8,5),label,fill='#203c2f')
sheet.save(ROOT/'provenance/limbs-20261004/root-NE-tail-review.jpg',quality=95)

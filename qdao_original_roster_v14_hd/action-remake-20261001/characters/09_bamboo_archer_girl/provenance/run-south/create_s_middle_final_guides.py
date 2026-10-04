from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];o=R/'provenance/run-south/guides';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
for f in [5,6,13,14]:
 x=555 if f<9 else 445
 im=Image.new('RGB',(1024,1024),(249,248,242));d=ImageDraw.Draw(im)
 d.text((30,30),f'S{f:02}: ONLY THE SMALL BACKGROUND SUPPORT LEG',font=font,fill=(20,80,180))
 d.text((30,80),'Foot contact must be at y905. Other raised leg unchanged.',font=font,fill=(20,50,100))
 d.polygon([(415,650),(585,650),(585,720),(415,720)],outline=(200,200,200),width=4)
 d.line([(x,715),(x,779),(x,838)],fill=(20,100,220),width=20)
 d.polygon([(x-22,838),(x+22,838),(x+30,885),(x+20,905),(x-20,905),(x-30,885)],fill=(20,100,220))
 d.line([(x-45,907),(x+45,907)],fill=(20,100,220),width=5)
 d.text((x-130,936),'SUPPORT SOLE / y905',font=font,fill=(20,100,220))
 im.save(o/f'S-{f:02}-middle-final-guide.png')
print('stage3 guide915 desired image contact905 reference')

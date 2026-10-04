from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[2]
out=R/'provenance/run-south/guides';out.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for f in range(3,9):
 s=(f-1)//2+1; pair=0 if f%2 else 1
 leg={2:[(610,735),(600+pair*4,813+pair*5),(551,900)],3:[(610,735),(555+pair*5,816+pair*3),(503,878)],4:[(610,735),(516+pair*5,803+pair*3),(454,851)]}[s]
 sole={2:[(530,927),(596,950)],3:[(480,905),(548,928)],4:[(437,867),(501,900)]}[s]
 swing=[(535,720),(620+pair*7,728+pair*6),(665+pair*12,807+pair*9)]
 im=Image.new('RGB',(1024,1024),(249,248,242));d=ImageDraw.Draw(im)
 d.text((35,30),f'SE frame{f:02} / phase{s} / pose{pair+1}',font=font,fill=(25,40,55))
 d.text((35,60),'POSE GUIDE ONLY: keep sprite head/body/arms unchanged',font=font,fill=(25,40,55))
 d.text((35,100),'BLUE = far LEFT support, rooted at screen-right hip',font=font,fill=(20,100,220))
 d.text((35,130),'ORANGE = near RIGHT swing in foreground',font=font,fill=(230,100,25))
 d.ellipse((475,220,785,490),outline=(205,205,205),width=3)
 d.polygon([(533,509),(703,520),(652,730),(509,713)],outline=(205,205,205))
 d.line(leg,fill=(20,100,220),width=19,joint='curve')
 d.line([leg[-1],sole[0],sole[1]],fill=(20,100,220),width=18,joint='curve')
 for x,y in leg:d.ellipse((x-13,y-13,x+13,y+13),fill=(20,100,220))
 d.line(swing,fill=(230,100,25),width=26,joint='curve')
 d.line([swing[-1],(702+pair*10,851+pair*8)],fill=(230,100,25),width=30)
 for x,y in swing:d.ellipse((x-15,y-15,x+15,y+15),fill=(230,100,25))
 d.text((710,905),'Airborne right boot',font=font,fill=(180,80,15))
 d.text((max(90,sole[0][0]-150),sole[1][1]+28),'LEFT forefoot on ground',font=font,fill=(20,100,220))
 d.text((370,657),'RIGHT hip (near)',font=font,fill=(230,100,25))
 d.text((625,700),'LEFT hip (far)',font=font,fill=(20,100,220))
 im.save(out/f'SE-{f:02}-stance-guide.png')
 (out/f'SE-{f:02}-stance-guide.json').write_text(json.dumps({'purpose':'abstract joint reference only; no source sprite pixels used','frame':f,'supportHip':'farLEFT','supportChain':leg,'supportSole':sole,'swingChain':swing},indent=2),encoding='utf8')
print('6 independent guide files ready')


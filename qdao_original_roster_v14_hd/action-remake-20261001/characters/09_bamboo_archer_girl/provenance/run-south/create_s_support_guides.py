from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];o=R/'provenance/run-south/guides'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for f in [5,6,7,8,13,14]:
 side='LEFT' if f<9 else 'RIGHT';x=555 if f<9 else 445
 stage=4 if f in [7,8] else 3;y=875 if stage==4 else 930
 im=Image.new('RGB',(1024,1024),(249,248,242));d=ImageDraw.Draw(im)
 d.text((30,30),f'SOUTH{f:02}: edit BLUE support leg only / stage{stage}',font=font,fill=(20,45,60))
 d.text((30,70),'Preserve upper body and OTHER raised swing leg exactly.',font=font,fill=(30,45,60))
 d.text((30,110),f'{side} support remains the same anatomical leg.',font=font,fill=(20,100,220))
 d.ellipse((350,190,650,480),outline=(215,215,215),width=3)
 d.polygon([(400,490),(600,490),(588,712),(410,712)],outline=(215,215,215))
 pts=[(x,715),(x+(4 if f%2 else -4),y-135),(x,y-63)]
 d.line(pts,fill=(20,100,220),width=18)
 for px,py in pts:d.ellipse((px-10,py-10,px+10,py+10),fill=(20,100,220))
 d.polygon([(x-25,y-60),(x+25,y-60),(x+35,y-15),(x+22,y),(x-22,y),(x-35,y-15)],fill=(20,100,220))
 d.line([(x-35,y+3),(x+35,y+3)],fill=(20,100,220),width=5)
 d.text((x-145,y+28),'Same support forefoot contact',font=font,fill=(20,100,220))
 im.save(o/f'S-{f:02}-support-guide.png')
print('6 SOUTH support-only guides ready')


from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
r=Path(r'E:\work\image\qdao_chibi_roster_v12\review\site')
items=[('23_lantern_courier','灯穗小使'),('24_lu_dongbin','吕洞宾'),('25_lion_drum_guard','狮鼓护卫'),('26_osmanthus_healer','桂香药婆'),('27_ink_kite_ranger','墨鸢游侠'),('28_moon_rabbit_artificer','月兔机关师'),('29_he_xiangu','何仙姑'),('30_han_xiangzi','韩湘子')]
b=Image.new('RGB',(1600,940),'#eeeade');draw=ImageDraw.Draw(b);font=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',28)
for i,(cid,name) in enumerate(items):
 x=(i%4)*400;y=(i//4)*470
 im=Image.open(r/'assets/v12'/cid/'portrait.png').convert('RGBA').resize((400,400),Image.Resampling.LANCZOS)
 b.paste(im,(x,y+45),im);box=draw.textbbox((0,0),name,font=font);draw.text((x+(400-box[2])/2,y+12),name,font=font,fill='#263934')
b.save(r/'roster-final.jpg',quality=92)
print(str(r/'roster-final.jpg'))

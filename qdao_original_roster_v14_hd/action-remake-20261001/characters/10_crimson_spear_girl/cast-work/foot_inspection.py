from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent
frames=[1,5,7,9,11,10]
out=Image.new('RGB',(1200,1000),'#deded8');d=ImageDraw.Draw(out)
for j,n in enumerate(frames):
 im=Image.open(root/f'cast-E-{n:02d}.png').convert('RGBA')
 # Diagnostic-only zoom of existing native rear knee/boot; source pixels remain unchanged.
 box=(300,875,670,1254)
 crop=im.crop(box);crop.thumbnail((370,460))
 x=(j%3)*400;y=(j//3)*500
 out.paste(crop,(x,y+30),crop)
 d.text((x+8,y+8),f'cast E{n:02d} rear foot / diagnostic only',fill='black')
out.save(root/'foot-inspection-E.jpg',quality=94)
print(root/'foot-inspection-E.jpg')
for start in [1,9]:
 out=Image.new('RGB',(1600,700),'#deded8');d=ImageDraw.Draw(out)
 for j,n in enumerate(range(start,start+8)):
  im=Image.open(root/f'cast-W-{n:02d}.png').convert('RGBA')
  crop=im.crop((450,870,1080,1254));crop.thumbnail((395,310))
  x=(j%4)*400;y=(j//4)*350
  out.paste(crop,(x,y+30),crop);d.text((x+8,y+8),f'W{n:02d} rear foot / diagnostic only',fill='black')
 out.save(root/f'foot-inspection-W{start}.jpg',quality=94)

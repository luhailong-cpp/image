from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
out=Image.new('RGB',(1440,1240),(235,238,239));dr=ImageDraw.Draw(out)
for row,(n,prev,nxt) in enumerate([(7,6,8),(14,13,15)]):
 paths=[R/f'run/SE/{prev:02}.png',R/f'run/staging/video-axis-SE-{n:02}-v1-export.png',R/f'run/SE/{nxt:02}.png']
 for col,p in enumerate(paths):
  im=Image.open(p).convert('RGBA');x=col*480;y=row*620
  full=im.resize((400,400));out.paste(full,(x+40,y),full)
  leg=im.crop((210,700,850,1005)).resize((480,190));out.paste(leg,(x,y+400),leg)
  dr.text((x+15,y+598),f'SE/{[prev,n,nxt][col]:02} '+('NEW' if col==1 else 'neighbor'),fill=(150,20,20) if col==1 else (15,20,25))
out.save(R/'run/staging/video-axis-SE-repair-neighbors.jpg',quality=97)


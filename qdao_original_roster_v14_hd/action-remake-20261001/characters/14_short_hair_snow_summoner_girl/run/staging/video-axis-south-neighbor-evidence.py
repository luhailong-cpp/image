from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
groups=[('SE',[5,6,7,8],7),('SE',[12,13,14,15],14),('SW',[4,5,6,7],5)]
out=Image.new('RGB',(1920,960),(235,238,239));draw=ImageDraw.Draw(out)
for row,(d,nums,target) in enumerate(groups):
 for col,n in enumerate(nums):
  im=Image.open(R/f'run/{d}/{n:02}.png').convert('RGBA').crop((220,695,860,1005)).resize((480,260),Image.Resampling.LANCZOS)
  x=col*480;y=row*320;out.paste(im,(x,y),im)
  draw.text((x+15,y+275),f'{d}/{n:02}'+('  swing reversal candidate' if n==target else '  neighbor'),fill=(150,20,20) if n==target else (20,20,20))
  if n==target:draw.rectangle((x+2,y+2,x+477,y+305),outline=(180,40,40),width=3)
out.save(R/'run/staging/video-axis-south-neighbor-evidence.jpg',quality=97)


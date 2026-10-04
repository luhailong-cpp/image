from PIL import Image,ImageDraw
from pathlib import Path
root=Path(__file__).resolve().parents[2]
grid=Image.new("RGB",(1536,1600),"#25313d");draw=ImageDraw.Draw(grid)
for n in range(1,17):
 im=Image.open(root/f"frames/run/NE/{n:02}.png").convert("RGBA").resize((384,384))
 x=(n-1)%4*384;y=(n-1)//4*400
 draw.line((x,y+345,x+383,y+345),fill="#74919d")
 grid.paste(im,(x,y),im);draw.text((x+6,y+380),f"NE{n:02}",fill="white")
grid.save(root/"work/run-NE-cast/ne-contact-current.jpg",quality=96)

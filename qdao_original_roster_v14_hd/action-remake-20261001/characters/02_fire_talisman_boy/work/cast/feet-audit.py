from PIL import Image,ImageDraw
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for d in ["E","W"]:
 grid=Image.new("RGB",(1536,1120),"#28323d");draw=ImageDraw.Draw(grid)
 for n in range(1,17):
  im=Image.open(root/f"frames/cast/{d}/{n:02}.png").convert("RGBA")
  im=im.crop((160,650,960,1000)).resize((384,168))
  x=(n-1)%4*384;y=(n-1)//4*280
  grid.paste(im,(x,y+50),im);draw.text((x+8,y+8),f"{d}{n:02} feet crop - QA only",fill="white")
 grid.save(root/f"work/cast/feet-{d}-current.jpg",quality=95)
print("built feet QA crops; no formal changed")

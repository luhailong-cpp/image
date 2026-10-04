from PIL import Image, ImageDraw
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for d in ["E","W"]:
 out=Image.new("RGB",(1536,1536),(238,236,224))
 dr=ImageDraw.Draw(out)
 for i in range(16):
  im=Image.open(root/"runtime"/"cast"/d/f"{i:02d}.png").convert("RGBA").resize((384,384))
  x=(i%4)*384;y=(i//4)*384
  out.paste(im,(x,y),im);dr.text((x+10,y+10),f"{d} {i:02d}",fill=(20,40,60))
  dr.line((x,y+353,x+384,y+353),fill=(60,120,170),width=1)
 out.save(root/"review"/f"cast_{d}_contact_20261003.jpg",quality=94)
print("contact previews generated without altering runtime")


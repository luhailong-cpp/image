from pathlib import Path
from PIL import Image,ImageDraw
import json
B=Path(__file__).parent
selected={d:{n:Path(json.loads((B/"selection.json").read_text())["slots"][f"attack/{d}/{n:02d}"]).name for n in range(1,13)} for d in ["E","W"]}
for d in ["E","W"]:
 sheet=Image.new("RGB",(1600,1200),(45,55,65)); dr=ImageDraw.Draw(sheet)
 for i in range(12):
  im=Image.open(B/selected[d][i+1]).convert("RGBA").resize((380,380),Image.Resampling.LANCZOS)
  x=(i%4)*400+10;y=(i//4)*400+15
  sheet.paste(im,(x,y),im)
  dr.text((x+8,y+5),f"{d} {i+1:02d}",fill="white")
 sheet.save(B/f"contact-{d}.jpg",quality=94)
print("Created selected 24 and contact-E/W")

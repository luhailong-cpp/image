from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl")
out=root/"audit/foot-axis-20261003"
out.mkdir(exist_ok=True)
sources=[]
for d in ["W","S","SE"]:
 for start in [1,9]:
  sheet=Image.new("RGB",(2048,448),(234,236,231));dr=ImageDraw.Draw(sheet)
  for j,f in enumerate(range(start,start+8)):
   p=root/f"runtime/run/{d}/{f:02d}.png"
   im=Image.open(p).convert("RGBA")
   crop=im.crop((0,620,1024,1024)).resize((512,202),Image.Resampling.LANCZOS)
   x=(j%4)*512;y=(j//4)*224
   sheet.paste(crop,(x,y+22),crop)
   h=hashlib.sha256(p.read_bytes()).hexdigest()
   dr.text((x+6,y+5),f"{d}/{f:02d}  {h[:12]}",fill=(20,35,20))
   sources.append({"slot":f"run/{d}/{f:02d}","sha256":h})
  sheet.save(out/f"{d}-{start:02d}-legs.png")
(out/"sources.json").write_text(json.dumps({"purpose":"Analysis-only lower-body crops, unmodified runtime sources; not asset edits.","sources":sources},indent=2),encoding="utf-8")
print(str(out))

from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).parent
s=json.loads((B/"selection.json").read_text())
C=Image.new("RGB",(1280,1392),(34,39,46)); d=ImageDraw.Draw(C)
out=[]
for i,(slot,p) in enumerate(s["slots"].items()):
 im=Image.open(B.parent/p).convert("RGBA"); a=im.getchannel("A"); box=a.point(lambda v:255 if v>=32 else 0).getbbox()
 row={"slot":slot,"source":p,"size":im.size,"alpha32BBox":box,"edgeTouch": bool(box and (box[0]==0 or box[1]==0 or box[2]==im.width or box[3]==im.height)),"sha256":hashlib.sha256((B.parent/p).read_bytes()).hexdigest()}
 out.append(row)
 tile=im.resize((320,320),Image.Resampling.LANCZOS)
 x=(i%4)*320;y=(i//4)*348
 C.paste(tile,(x,y),tile)
 d.line((x,y+1160*320/1254,x+320,y+1160*320/1254),fill=(76,110,110))
 d.text((x+4,y+322),slot+" "+Path(p).name,fill="white")
C.save(B/"contact-current.jpg",quality=95)
(B/"geometry-current.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print(json.dumps(out,indent=2))


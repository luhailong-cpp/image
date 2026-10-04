from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).parent
R=B.parent
root=json.loads((R/"source-selection.json").read_text(encoding="utf-8"))["slots"]
own=json.loads((B/"selection.json").read_text(encoding="utf-8"))["slots"]
slots={**root,**own};sheet=Image.new("RGB",(1280,1360),(34,42,46));draw=ImageDraw.Draw(sheet)
rows=[]
for i in range(16):
 key=f"run/NE/{i+1:02d}";x=(i%4)*320;y=(i//4)*340
 rel=slots.get(key)
 if rel and (p:=R/rel).exists():
  im=Image.open(p).convert("RGBA").resize((320,320),Image.Resampling.LANCZOS);sheet.paste(im,(x,y),im);rows.append(dict(slot=key,file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 draw.line((x,y+int(1155/1254*320),x+319,y+int(1155/1254*320)),fill=(93,115,111))
 draw.text((x+4,y+322),key+(" selected" if rel else " pending root"),fill="white")
sheet.save(B/"contact-current.jpg",quality=94)
(B/"contact-current.jpg.generation.json").write_text(json.dumps(dict(operation="full native canvas downscale into contact cells, no asset modification",groundDiagnosticNativeY=1155,sources=rows),indent=2),encoding="utf-8")
print(json.dumps({"shown":len(rows),"own":len(own)}))


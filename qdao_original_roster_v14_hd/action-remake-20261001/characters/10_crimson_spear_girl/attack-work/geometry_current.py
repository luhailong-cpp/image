from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).parent
slots=json.loads((B/"selection.json").read_text(encoding="utf-8"))["slots"]
rows=[]
for key,rel in slots.items():
 p=B.parent/rel; im=Image.open(p); a=im.getchannel("A")
 bb=a.point(lambda x:255 if x>=32 else 0).getbbox()
 rows.append(dict(slot=key,file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=list(im.size),mode=im.mode,alphaExtrema=a.getextrema(),bboxAlpha32=bb,mainEdgeTouch=bool(bb and (bb[0]==0 or bb[1]==0 or bb[2]==im.width or bb[3]==im.height))))
(B/"geometry-current.json").write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),selected=len(rows),duplicateSha=len(rows)!=len({r["sha256"] for r in rows}),frames=rows),indent=2),encoding="utf-8")
for d in ["E","W"]:
 sources=[r for r in rows if r["slot"].split("/")[1]==d]
 (B/("contact-"+d+".jpg.generation.json")).write_text(json.dumps(dict(operation="whole-canvas contact preview only",nativeImageEdits=False,cellSize=[380,380],sources=sources),indent=2),encoding="utf-8")
print(json.dumps(dict(selected=len(rows),mainEdgeTouch=[r["slot"] for r in rows if r["mainEdgeTouch"]],bounds={r["slot"]:r["bboxAlpha32"] for r in rows})))


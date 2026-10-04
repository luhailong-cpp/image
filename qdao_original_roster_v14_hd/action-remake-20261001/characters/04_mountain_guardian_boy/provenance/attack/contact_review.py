from pathlib import Path
from PIL import Image, ImageDraw
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]
for d in ("E","W"):
 files=sorted((ROOT/"frames"/"attack"/d).glob("frame_*.png"))
 out=ROOT/"provenance"/"attack"/f"{d}_contact.png"
 canvas=Image.new("RGB",(1536,3*408),(246,242,225));draw=ImageDraw.Draw(canvas);refs=[]
 for i,p in enumerate(files):
  im=Image.open(p).convert("RGBA").resize((384,384),Image.Resampling.LANCZOS);x=(i%4)*384;y=(i//4)*408
  canvas.paste(im,(x,y+24),im);draw.text((x+8,y+5),p.stem,fill=(15,40,20))
  refs.append({"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
 canvas.save(out)
 out.with_suffix(".png.generation.json").write_text(json.dumps({"file":out.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"operation":"deterministic_preview_contact_sheet","modelGenerated":False,"createdAt":datetime.now(timezone.utc).isoformat(),"derivedFrom":refs},ensure_ascii=False,indent=2),encoding="utf-8")
 print(out)


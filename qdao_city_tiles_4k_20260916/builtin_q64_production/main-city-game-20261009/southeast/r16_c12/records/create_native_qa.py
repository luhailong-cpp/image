from pathlib import Path
import json,hashlib
from PIL import Image
t=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r16_c12")
a=json.loads((t/"candidate/latest-assembly.json").read_text(encoding="utf-8"))
base=Image.open(a["candidate"]["path"]).convert("RGB")
d=t/"review"/"native-qa-20261016";d.mkdir(exist_ok=True)
for axis in ("v","h"):
 for seam in (1024,2048,3072):
  for q in range(4):
   box=(seam-256,q*1024,seam+256,(q+1)*1024) if axis=="v" else (q*1024,seam-256,(q+1)*1024,seam+256)
   p=d/f"{axis}{seam}-q{q}.png"
   if not p.exists():base.crop(box).save(p)
east=Image.open(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r16_c13/candidate/r16_c13-4k-orphan-repair-v2-20261013.png").convert("RGB")
for q in range(4):
 p=d/f"east-join-q{q}.png"
 im=Image.new("RGB",(768,1024));im.paste(base.crop((3712,q*1024,4096,(q+1)*1024)),(0,0));im.paste(east.crop((0,q*1024,384,(q+1)*1024)),(384,0))
 if not p.exists():im.save(p)
n=t.parent/"r15_c12/progress.json"
if n.exists():
 pr=json.loads(n.read_text(encoding="utf-8-sig"))
 if pr.get("candidate") and Path(pr["candidate"]).exists():
  north=Image.open(pr["candidate"]).convert("RGB")
  for q in range(4):
   p=d/f"north-join-q{q}.png"
   im=Image.new("RGB",(1024,768));im.paste(north.crop((q*1024,3712,(q+1)*1024,4096)),(0,0));im.paste(base.crop((q*1024,0,(q+1)*1024,384)),(0,384))
   if not p.exists():im.save(p)
print(str(d))

from pathlib import Path
import json,hashlib
from PIL import Image
T=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast")/"r13_c11"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=T/"selected-patches.json";d=json.loads(s.read_text())
backup=T/"selected-before-recovered-20261016-v1.json"
assert not backup.exists();backup.write_bytes(s.read_bytes())
recovered=[]
for pid,v in [("p22","v2"),("p34","v1")]:
 p=T/"native"/f"{pid}-{v}.png";g=json.loads(p.with_suffix(".png.generation.json").read_text());r=json.loads((T/f"{pid}-{v}.receipt.json").read_text())
 assert sha(p)==sha(r["sourcePath"])==g["sha256"]
 assert Image.open(p).size==(1254,1254)
 d["patches"][pid]=f"native/{pid}-{v}.png";recovered.append({"patch":pid,"sha256":sha(p),"receipt":str(T/f"{pid}-{v}.receipt.json")})
d.update(internalReady=False,formalAccepted=False,materialPending=True)
s.write_text(json.dumps(d,indent=2))
(T/"recovered-returned-20261016-v1.json").write_text(json.dumps({"recovered":recovered,"selectedCount":len(d["patches"]),"note":"p22-v2 follows intended rock layout; bottom foam and stone silhouette transition remain pending, no new generation for already returned assets."},indent=2))
print(len(d["patches"]))


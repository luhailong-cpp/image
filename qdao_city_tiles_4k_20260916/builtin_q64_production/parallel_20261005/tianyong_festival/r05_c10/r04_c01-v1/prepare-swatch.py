from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");src=D.parent/"r04_c02-v1/final-v3/joined.png";p=D/"nearby-native-material-swatch.png";Image.open(src).crop((0,400,600,1000)).save(p)
ref=lambda f:{"file":str(f),"sha256":hashlib.sha256(Path(f).read_bytes()).hexdigest()}
(p.with_suffix(".png.generation.json")).write_text(json.dumps({"source":ref(src),"output":ref(p),"cropLTRB":[0,400,600,1000],"nativeScale":1,"newModelCalls":0,"operation":"Exact native nearby map material crop only"},indent=2),encoding="utf-8")
r=json.loads((D/"request.json").read_text(encoding="utf-8"));r["payload"]["referenced_image_paths"][1]=str(p);(D/"request.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
prep=json.loads((D/"preparation.json").read_text(encoding="utf-8"));prep["references"]=[ref(f) for f in r["payload"]["referenced_image_paths"]];(D/"preparation.json").write_text(json.dumps(prep,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(r["payload"]))


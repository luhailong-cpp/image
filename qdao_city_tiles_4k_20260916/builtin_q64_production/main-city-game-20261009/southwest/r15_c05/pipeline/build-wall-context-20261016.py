from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[2]
s=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/tianyong/tianyong-spring-natural-stone-v9.png')
p=B/'r15_c05/pipeline/guides/wall-layout-context-20261016-v01.png'
assert not p.exists()
box=(280,1125,405,1200)
Image.open(s).crop(box).resize((1000,600),Image.Resampling.NEAREST).save(p)
d={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':str(s),'sourceSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'cropBox':box,'operation':'nearest enlarged layout-context only, not game art','formalAccepted':False}
Path(str(p)+'.derivation.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d))

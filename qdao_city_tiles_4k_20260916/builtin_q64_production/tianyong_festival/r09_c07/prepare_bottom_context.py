from pathlib import Path
from PIL import Image
import json,hashlib
p=Path(r'E:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\r09_c07')
record=json.loads((p/'layout-record.json').read_text())
src=Image.open(record['layoutSource']).convert('RGB')
a=src.resize((4326,4326),Image.Resampling.BICUBIC,box=tuple(record['layoutSourceBoxLTRB']))
neighbor=p.parent/'quad_r10_c07_c10/output_v2/extended-context.png'
a.paste(Image.open(neighbor).convert('RGB').crop((0,0,4326,230)),(0,4096))
a.resize((1254,1254),Image.Resampling.LANCZOS).save(p/'layout-input.jpg',quality=85)
record['styleInputBottomNeighborSource']=str(neighbor);record['styleInputBottomNeighborSourceSha256']=hashlib.sha256(neighbor.read_bytes()).hexdigest();record['bottomNativeReferenceBoxLTRB']=[0,0,4326,230];record['styleInputMethod']='Reference-only canvas with exact230px next-row overlap pasted at bottom, then downsample for mother-reference generation.'
(p/'layout-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')

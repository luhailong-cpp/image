from pathlib import Path
from PIL import Image
import hashlib,json,datetime
O=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r11_c15/qa-independent/rail-finish');O.mkdir(parents=True,exist_ok=True)
s=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r11_c15/repairs/internal/r11_c15-internal-candidate-v5.png')
p=O/'input.png';Image.open(s).crop((1600,2200,2854,3454)).save(p)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={'file':str(p),'sha256':sha(p),'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','derivedFrom':[{'file':str(s),'sha256':sha(s),'generationRecord':str(s)+'.generation.json'}],'operation':{'method':'native integer crop','crop':[1600,2200,2854,3454],'resampling':False}}
Path(str(p)+'.generation.json').write_text(json.dumps(d,indent=2),encoding='utf8')


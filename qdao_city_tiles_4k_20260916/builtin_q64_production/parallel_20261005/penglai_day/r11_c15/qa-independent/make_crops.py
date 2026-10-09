from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r11_c15')
src=R/'repairs/internal/r11_c15-internal-candidate-v5.png'
out=R/'qa-independent';out.mkdir(exist_ok=True)
im=Image.open(src)
rec={'source':str(src),'sourceSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'method':'native integer crop; no resize or pixel edit','crops':[]}
for name,box in [('rail-upper-step',[2040,2378,2440,2778]),('rail-lower-step',[2033,3003,2433,3403]),('boom-tint-return',[2480,1860,2880,2260]),('rail-lower-right',[2276,3127,2676,3527])]:
 p=out/(name+'.png');im.crop(box).save(p);rec['crops'].append({'path':str(p),'bbox':box})
(out/'qa-crops-source.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
print(rec['sourceSHA256'])

from pathlib import Path
from PIL import Image
import hashlib,json,shutil
p=Path(r'E:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\quad_r10_c07_c10')
d=p/'repairs/v2'
for f in ('inputs','native','prompts'): (d/f).mkdir(parents=True,exist_ok=True)
a=Image.open(p/'output/quad_16384x4096_candidate.png')
entries=[]
for ident,box in [('boundary_lower',(11661,2048,12915,3302)),('stairs_boundary',(11661,2842,12915,4096))]:
 f=d/'inputs'/f'{ident}.png';a.crop(box).save(f)
 a.crop(box).save(d/'inputs'/f'{ident}.jpg',quality=85)
 entries.append({'id':ident,'cropLTRB':box,'pixels':[1254,1254],'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(d/'input-plan.json').write_text(json.dumps({'source':str(p/'output/quad_16384x4096_candidate.png'),'entries':entries},indent=2),encoding='utf-8')
print('Two original-pixel repair inputs ready')

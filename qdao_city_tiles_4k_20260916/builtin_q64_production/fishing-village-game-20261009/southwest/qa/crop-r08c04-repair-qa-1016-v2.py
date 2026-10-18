import json,hashlib,sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
trace=json.loads((q/'repair-r08c04-1016-v2-trace.json').read_text())
im=Image.open(trace['candidate']['path'])
out=[]
for key in 'abc':
 r=json.loads((z/'native'/('r08_c04_repair_'+key+'_1016_v1.request.json')).read_text(encoding='utf-8-sig'))
 box=r['coordinates']['tileContextBox'];p=q/('repair-r08c04-1016-v2-'+key+'-after-1254.png');assert not p.exists();im.crop(box).save(p);out.append({'id':key,'file':p.as_posix(),'sha256':sha(p),'sourceBox':box,'operation':'integer crop only'})
p=q/'repair-r08c04-1016-v2-local-qa.json';assert not p.exists();p.write_text(json.dumps({'source':trace['candidate'],'crops':out},indent=2),encoding='utf-8')


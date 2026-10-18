from pathlib import Path
from PIL import Image
import json,hashlib
W=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest/work-r06_c02');im=Image.open(W/'ground-v1/r06_c02.candidate.png');q=W/'ground-v1/qa';q.mkdir(exist_ok=True)
records=[]
for j in range(1,4):
 for k in range(4):
  for typ,box in [('v',(j*1024-240,k*1024,j*1024+240,(k+1)*1024)),('h',(k*1024,j*1024-240,(k+1)*1024,j*1024+240))]:
   name=f'{typ}{j}-{k+1}.png';old=Image.open(W/'base-v2/qa'/name);new=im.crop(box)
   same=old.tobytes()==new.tobytes()
   if not same:new.save(q/name)
   records.append({'file':name,'unchangedFromBaseV2':same,'sha256':hashlib.sha256(new.tobytes()).hexdigest()})
(q/'reuse.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records))


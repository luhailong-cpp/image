from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08/c02-north-repair');O=R/'seat-compare';O.mkdir(exist_ok=True)
for name,p,b in [('base',R/'original/native/r01_c02.png',(600,220,900,430)),('wood02',R/'wood-source02.png',(600,732,900,942))]:
 im=Image.open(p).convert('RGB').crop(b);out=O/(name+'.png');assert not out.exists();im.save(out)
(O/'manifest.json').write_text(json.dumps({'operation':'integer crops only','baseSourceBox':[600,220,900,430],'wood02SourceBox':[600,732,900,942]},indent=2))


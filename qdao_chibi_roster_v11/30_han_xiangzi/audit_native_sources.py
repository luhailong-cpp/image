from pathlib import Path
import importlib.util,json,numpy as np
from PIL import Image
char=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('sp',Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
r={}
for p in sorted((char/'sources').glob('walk_*_2x2.png')):
 im=Image.open(p).convert('RGBA');clean=sp.remove_bg_magenta(im.copy());cs=sp.connected_components(clean,min_area=500)
 r[p.stem]={'size':list(im.size),'components':len(cs),'boxes':[c['bbox'] for c in cs],'native_edge_touches':sum(c['touches_edge'] for c in cs)}
 print(p.name,r[p.stem])
(char/'processing/native-source-audit.json').write_text(json.dumps(r,indent=2),encoding='utf8')

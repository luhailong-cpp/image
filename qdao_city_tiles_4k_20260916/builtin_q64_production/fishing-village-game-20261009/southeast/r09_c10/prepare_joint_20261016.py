from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
Q=T/'qa/joint-20261016-v1';Q.mkdir(exist_ok=True)
sel=json.loads((T/'selected-patches.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.new('RGB',(4096,4096));sources=[]
for pid,rel in sel['patches'].items():
 p=T/rel;im.paste(Image.open(p).crop((115,115,1139,1139)),((int(pid[2])-1)*1024,(int(pid[1])-1)*1024));sources.append(dict(patch=pid,file=str(p),sha256=sha(p)))
box=[397,1721,1651,2975]
p=Q/'stone-joint-input-1254.png';assert not p.exists();im.crop(box).save(p)
d=dict(file=str(p),sha256=sha(p),tileBox=box,operation='Exact unscaled current selected native core pixels; input only',sources=sources)
p.with_suffix('.png.derivation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps(d))

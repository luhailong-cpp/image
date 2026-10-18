from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
Z=Path(__file__).resolve().parents[1]
old=Z/'tiles/r06_c03_candidate-v7_4096.png';new=Z/'tiles/connected-r05-r06-cross-v5/r06_c03_rail-ground-v1_4096.png'
a=np.array(Image.open(old).convert('RGB'));b=np.array(Image.open(new).convert('RGB'))
d=np.any(a[:,:115]!=b[:,:115],axis=2);ys,xs=np.where(d)
info=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
data=dict(tileId='r06_c03',comparison='west115 all4096 rows exact RGB',old=info(old),current=info(new),exactPixelsUnchanged=bool(not d.any()),changedPixels=int(d.sum()),changedBoxHalfOpen=None if not d.any() else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)])
out=Z/'qa/r06_c03_cross_v5_west115_vs_v7_20261016.json'
assert not out.exists();out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(report=info(out),**data)))


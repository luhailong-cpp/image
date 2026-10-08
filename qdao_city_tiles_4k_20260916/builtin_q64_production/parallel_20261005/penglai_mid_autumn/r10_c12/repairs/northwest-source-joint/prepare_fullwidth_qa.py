from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
m=read(T/"output/manifest.json");e=Image.open(m["file"]).convert("RGB");n=Image.open(m["northSource"]).convert("RGB");sources=[ref(m["file"]),ref(m["northSource"])]
for i,(lo,hi,above,below) in enumerate([(0,1024,160,160),(1024,2048,160,160),(2048,3072,160,160),(3072,4096,160,160),(960,1600,80,100),(1152,1408,40,70)]):
 p=D/("qa-current-fullwidth-%d.png"%(i+1));assert not p.exists();im=Image.new("RGB",(hi-lo,above+below));im.paste(n.crop((lo,4096-above,hi,4096)),(0,0));im.paste(e.crop((lo,0,hi,below)),(0,above));im.save(p);write(str(p)+".generation.json",dict(**ref(p),sources=sources,operation=dict(topCropLTRB=[lo,4096-above,hi,4096],bottomCropLTRB=[lo,0,hi,below],joinY=above),nativeScale=1,actuallyViewed=False))
print(str(D))


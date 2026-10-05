"""Reproduce v2 and v3 by native-size compositing; no AI generation."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for version in ("v2","v3"):
    folder=HERE/version
    record=json.loads((folder/"r08_c08.png.generation.json").read_text())
    source=record["derivedFrom"][0]; patchsource=record["derivedFrom"][1]
    bp=Path(source["file"]); pp=Path(patchsource["file"])
    assert sha(bp)==source["sha256"] and sha(pp)==patchsource["sha256"]
    base=np.array(Image.open(bp).convert("RGB"))
    patch=np.array(Image.open(pp).convert("RGB"))
    assert base.shape==(4096,4096,3) and patch.shape==(1254,1254,3)
    y,x=np.mgrid[:1254,:1254]
    edge=np.minimum.reduce([x,y,1253-x,1253-y])
    t=np.clip((edge-24)/160,0,1)
    alpha=np.rint(t*t*(3-2*t)*255).astype(np.uint8)[:,:,None]
    x0,y0,x1,y1=record["cropLTRB"]
    context=base[y0:y1,x0:x1].copy()
    base[y0:y1,x0:x1]=((context.astype(np.uint32)*(255-alpha)+patch.astype(np.uint32)*alpha+127)//255).astype(np.uint8)
    out=folder/"r08_c08.png"
    Image.fromarray(base).save(out)
    assert sha(out)==record["sha256"]
    print(version+" reproduced byte-identically")


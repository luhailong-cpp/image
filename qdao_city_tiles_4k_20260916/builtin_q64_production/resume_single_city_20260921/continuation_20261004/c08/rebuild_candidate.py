"""Rebuild this work-in-progress candidate; native dimensions retained."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SESSION = HERE.parent.parent
BASE = SESSION / "continuation_20260925T132104Z/repairs/c08-top-v1/r08_c08.png"
NATIVE = HERE / "cross-repair.native.png"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(BASE) == "48dbdc0d6f812461de8b4192928355af6ac215b31cb11a80894474cd305a1131"
assert sha(NATIVE) == "e7a58a4dcb264a8af56f6b93b6c69cfe0826138cc4c46c50c4626a04c4656e37"
base = np.array(Image.open(BASE).convert("RGB"))
patch = np.array(Image.open(NATIVE).convert("RGB"))
assert base.shape == (4096,4096,3) and patch.shape == (1254,1254,3)
y,x = np.mgrid[:1254,:1254]
edge = np.minimum.reduce([x,y,1253-x,1253-y])
v = np.clip((edge-24)/160,0,1)
alpha = np.rint(v*v*(3-2*v)*255).astype(np.uint8)
context = base[2445:3699,397:1651].copy()
mixed = ((context.astype(np.uint32)*(255-alpha[:,:,None])+patch.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
base[2445:3699,397:1651] = mixed
Image.fromarray(base).save(HERE/"r08_c08.png")
assert sha(HERE/"r08_c08.png") == "e80b347a5945119adcffc9c2ebf023129a145bcfa87f672ce52288aaa971c65f"
print("Candidate reproduced byte-identically; not production accepted.")


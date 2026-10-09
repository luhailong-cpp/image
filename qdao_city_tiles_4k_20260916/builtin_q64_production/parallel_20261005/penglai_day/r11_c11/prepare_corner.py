from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import helper as h
d=T/'repairs/corner-joint';src=d/'corner-target.png';a=np.array(Image.open(src));m=np.zeros(a.shape[:2],bool)
m[557:697,440:1050]=True;m[420:1030,557:697]=True
a[m]=[255,0,255];dest=d/'corner-gap-target.png';Image.fromarray(a).save(dest);h.p.derived(dest,[src],{'method':'magenta missing input guide for native fourtile artificial rock seam; not final art','gapRectangles':[[440,557,1050,697],[557,420,697,1030]]})


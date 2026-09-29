from pathlib import Path
from PIL import Image
import json,numpy as np
r=Path(__file__).resolve().parents[1]
sel=json.loads((r/'10-work/selection-current.json').read_text(encoding='utf-8-sig'))
for s,v in sel.items():
 a=np.asarray(Image.open(r/'10-generation'/v['archive']/'raw.png').convert('RGBA'))[:,:,3]
 b=[int(a[0].max()),int(a[-1].max()),int(a[:,0].max()),int(a[:,-1].max())]
 if max(b)>8: print(json.dumps({'slot':s,'archive':v['archive'],'boundaryMax':b,'pixelCountAbove8':int((a[0]>8).sum()+(a[-1]>8).sum()+(a[:,0]>8).sum()+(a[:,-1]>8).sum())}))

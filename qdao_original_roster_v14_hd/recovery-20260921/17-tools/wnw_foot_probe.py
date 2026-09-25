"""Read-only lower-bound review aids for W/NW final selections; not gait approval."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
BASE=Path(__file__).resolve().parent.parent
sel=json.loads((BASE/'17-delivery-preview/wnw-selections-20260923-v2.json').read_text(encoding='utf-8'))
rows=[]
for slot,data in sel['overrides'].items():
 rec=json.loads(Path(data['import_result']).read_text(encoding='utf-8'))
 a=np.array(Image.open(rec['path']).convert('RGBA'))
 yy,xx=np.where(a[:,:,3]>8)
 low=yy.max()
 # W boots lie left of x630; hanging scroll ends farther right. Only a probe.
 boot_mask=(a[:,:,3]>8)&(np.indices(a.shape[:2])[1]<630)&(np.indices(a.shape[:2])[0]>800)
 by,bx=np.where(boot_mask)
 rows.append({'slot':slot,'top':int(yy.min()),'bottom':int(low),'bottom_x_range':[int(xx[yy==low].min()),int(xx[yy==low].max())],'W_boot_region_bottom':int(by.max()) if slot.split('/')[1]=='W' and len(by) else None})
print(json.dumps(rows,indent=2))


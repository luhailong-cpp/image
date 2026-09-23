from pathlib import Path
import json
import numpy as np
from PIL import Image
base=Path(r'D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/recovery-20260921')
sel=json.loads((base/'17-tools/selections-S-SW-v2.json').read_text(encoding='utf-8'))
rows=[]
for slot,data in sel['overrides'].items():
 rec=json.loads(Path(data['import_result']).read_text(encoding='utf-8'))
 a=np.array(Image.open(rec['path']).convert('RGBA'))
 y,x=np.where(a[:,:,3]>8)
 boot=a[790:,250:670,3]>8
 by,bx=np.where(boot)
 bottom=int(y.max()); foot=int(by.max()+790)
 rows.append({'slot':slot,'top':int(y.min()),'bottom':bottom,'bottom_x':[int(x[y==bottom].min()),int(x[y==bottom].max())],'boot_bottom':foot,'accessory_below_boot':bottom-foot})
print(json.dumps(rows,indent=2))


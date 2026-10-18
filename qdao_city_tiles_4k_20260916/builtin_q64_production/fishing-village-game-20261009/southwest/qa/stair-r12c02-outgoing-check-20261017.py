import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def arr(r):
 assert ref(r['path'])['sha256']==r['sha256']
 return np.array(Image.open(r['path']).convert('RGB'))
idx={x['tile']:x for x in read(Z/'art-delivery-index.json')['artAccepted']}
tr=read(Q/'pair-r11c02-r12c02-v1-trace.json');fresh={x['tile']:x for x in tr['tiles']}
old=arr(idx['r11_c02']['nativeContext']);new=arr(fresh['r11_c02']['context']);east=arr(idx['r11_c03']['nativeContext'])
delta=np.any(old!=new,axis=2);yy,xx=np.where(delta)
out=Q/'pair-r11c02-r12c02-v1-east-bottom-direct-100pct.png';assert not out.exists()
Image.fromarray(np.concatenate([new[3311:4211,3866:4211],east[3311:4211,115:460]],axis=1)).save(out)
southold=arr(read(Q/'full-tile-r12_c02-assembly.json')['context']);southnew=arr(fresh['r12_c02']['context'])
d=np.any(southold!=southnew,axis=2);ys,xs=np.where(d)
r={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'northInput':idx['r11_c02']['nativeContext'],'eastInput':idx['r11_c03']['nativeContext'],'northNew':fresh['r11_c02']['context'],'northChangedBoundingBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'southChangedBoundingBox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'northContextStripUnchanged':bool(np.array_equal(old[:230],new[:230])),'northEastBeforeBottomOverlapUnchanged':bool(np.array_equal(old[:4096,3866:],new[:4096,3866:])),'southBelowTopOverlapUnchanged':bool(np.array_equal(southold[230:],southnew[230:])),'eastBottomDirectQa':ref(out),'qaOperation':'integer crops and direct paste of outgoing core pixels; no resampling','qaBoundaryX':345}
p=Q/'pair-r11c02-r12c02-v1-outgoing-edge-check.json'
with p.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps(r))


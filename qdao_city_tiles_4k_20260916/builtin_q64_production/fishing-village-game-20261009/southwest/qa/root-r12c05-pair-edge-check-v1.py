import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
z=Path(__file__).resolve().parent.parent;qa=z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def arr(p):return np.array(Image.open(p).convert('RGB'))
idx={x['tile']:x for x in read(z/'art-delivery-index.json')['artAccepted']}
tr=read(qa/'pair-r11c05-r12c05-v1-trace.json'); fresh={x['tile']:x for x in tr['tiles']}
old=arr(idx['r11_c05']['nativeContext']['path']);new=arr(fresh['r11_c05']['context']['path']);east=arr(idx['r11_c06']['nativeContext']['path'])
delta=np.any(old!=new,axis=2);yy,xx=np.where(delta)
out=qa/'pair-r11c05-r12c05-v1-east-bottom-direct-100pct.png';assert not out.exists()
Image.fromarray(np.concatenate([new[3311:4211,3866:4211],east[3311:4211,115:460]],axis=1)).save(out)
r={'inputCurrentC05':idx['r11_c05']['nativeContext'],'inputCurrentC06':idx['r11_c06']['nativeContext'],'newC05':fresh['r11_c05']['context'],'changedBoundingBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'northContextStripUnchanged':bool(np.array_equal(old[:230],new[:230])),'eastBeforeBottomOverlapUnchanged':bool(np.array_equal(old[:4096,3866:],new[:4096,3866:])),'eastBottomDirectQa':ref(out),'qaOperation':'integer crops and side-by-side paste of exact outgoing core pixels; no resampling','qaBoundaryX':345}
p=qa/'pair-r11c05-r12c05-v1-outgoing-edge-check.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))

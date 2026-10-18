from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
old=Q/'pair-r10c03-r11c03-v1-r11_c03-context-native.png';new=Q/'pair-r11c02-c03-v1-r11_c03-context-native.png';north=Q/'pair-r10c03-r11c03-v1-r10_c03-context-native.png'
a=np.array(Image.open(old).convert('RGB'));b=np.array(Image.open(new).convert('RGB'));n=np.array(Image.open(north).convert('RGB'))
d=np.any(a[:230]!=b[:230],axis=2);ys,xs=np.where(d)
print({'northHaloChangedPixels':int(d.sum()),'box':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
v=np.concatenate([n[3866:4211,0:1015],b[115:460,0:1015]],axis=0)
p=Q/'pair-r11c02-c03-v1-c03-northwest-recheck-100pct.png';assert not p.exists();Image.fromarray(v).save(p)
t={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'pending_visual_review','priorC03':ref(old),'currentC03':ref(new),'northC03':ref(north),'northHaloChangedPixelCount':int(d.sum()),'northHaloChangedContextBox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'qa':ref(p),'method':'Native 1015x690 crop including canonical north tile edge and west halo: north context [0,3866,1015,4211] above new south context [0,115,1015,460]; no resampling.','unaffectedNorthEdgeContextXStart':int(xs.max()+1) if len(xs) else 0,'priorAudit':ref(Q/'pair-r10c03-r11c03-v1-art-audit-v1.json')}
p=Q/'pair-r11c02-c03-v1-c03-northwest-recheck-data.json';assert not p.exists();p.write_text(json.dumps(t,indent=2)+'\n');print(json.dumps(t))

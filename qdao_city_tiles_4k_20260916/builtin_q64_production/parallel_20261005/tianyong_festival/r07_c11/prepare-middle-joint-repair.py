from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
N=Path(__file__).resolve().parent;D=N/'middle-joint-repair-v1';D.mkdir(exist_ok=False)
R=N/'full-review-root-v016';I=json.loads((R/'review-image-index.json').read_text());src=I['source'];S=Image.open(src['file']).convert('RGBA')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
assert sha(src['file'])==src['sha256']
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
box=[1300,1350,2324,2374];roi=[1630,1770,2050,2140];local=[roi[0]-box[0],roi[1]-box[1],roi[2]-box[0],roi[3]-box[1]]
C=S.crop(box);C.save(D/'original-context.png');a=np.array(C);x1,y1,x2,y2=local;a[y1:y2,x1:x2]=0;Image.fromarray(a).save(D/'edit-context.png')
mask=Image.new('L',(1024,1024));mask.paste(255,tuple(local));mask.save(D/'repair-roi-mask.png')
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
prompt='Precise local native map repair. IMAGE1 is the exact1024x1024 edit target with one transparent rectangular hole. IMAGE2 is its original before-image for geometry. IMAGE3 is approved Q Daoist game STYLE ONLY. Fill the hole and return exact1024x1024 same-scale opaque output; leave everything outside the hole unchanged. Fix one specific defect: the broad stone paving joint enters from the left around y720, curves upward then tapers into a floating point below the bridge shadow. Repaint this locally into ONE continuous clean rounded architectural joint: follow the existing incoming lower-left paving groove upward and curve it naturally to JOIN the underside/base boundary of the ivory bridge near x650,y500. The groove must terminate at the actual bridge-base boundary, separating two coherent stone slabs, not fade into unbroken stone. Preserve the existing bridge column/base outline, its soft tree shadow, all other joints and illumination. Keep the left incoming groove thickness and ivory bevel highlight matching the neighbors. Clean smooth rounded hand-painted ivory, muted warm groove, no cracks, chipped triangles, fine veining or extra detail. Do not change architecture or add decor. Do not blur away the groove. No geometric transform, no resize, zoom, recolor, frame or text.'
req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':src,'sourceReview':ref(R/'native-review-with-finding.json'),'windowTileLocalLTRB':box,'repairTileLocalLTRB':roi,'repairLocalLTRB':local,'configSnapshot':json.loads((N/'r01_c04-v1/request.json').read_text())['configSnapshot'],'payload':{'prompt':prompt,'referenced_image_paths':[str(D/'edit-context.png'),str(D/'original-context.png'),str(style)],'transparent_background':False},'references':[ref(D/'edit-context.png'),ref(D/'original-context.png'),ref(style)],'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False}
save(D/'request.json',req);print(str(D))

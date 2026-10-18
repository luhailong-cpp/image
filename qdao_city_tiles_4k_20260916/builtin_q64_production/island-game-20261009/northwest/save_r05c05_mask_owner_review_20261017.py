import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pin=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
items=[]
for ver in [1,2]:
 p=Z/f'qa/r05_c05_r2r3_grout_shadow_a01_mask_v{ver}/mask_selection.json'
 s=json.loads(p.read_text());a=np.array(Image.open(s['target']['path']).convert('RGB'));b=np.array(Image.open(s['repair']['path']).convert('RGB'));m=np.array(Image.open(s['mask']['path']));c=np.array(Image.open(s['combinedCrop']['path']).convert('RGB'))
 for k in ['target','repair','mask','combinedCrop']:assert sha(s[k]['path'])==s[k]['sha256']
 assert set(np.unique(m)).issubset({0,255}) and np.array_equal(c,np.where((m==255)[:,:,None],b,a))
 items.append(dict(maskVersion=ver,selectionRecord=pin(p),combined=s['combinedCrop'],pixelSourceSelectionExact=True,actuallyViewedAtNativeScale=True,ownerVisualStatus='REJECT' if ver==1 else 'PROVISIONAL_PASS_AWAITING_INDEPENDENT_REVIEW',note='Introduces new blind groove ends near local(600,690)/(710,682); do not apply.' if ver==1 else 'Original middle-band blind corners and rectangular shadow cut closed; expanded lower selection avoids v1 blind ends. Check lower/left hard-selection boundary independently before adoption.',formalAccepted=False))
out=Z/'qa/r05_c05_r2r3_grout_shadow_a01_mask_owner_review_20261017.json'
with out.open('x',encoding='utf-8') as f:json.dump(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='right_continuation',reviews=items,materialStatus='PENDING',noFullTileAcceptance=True),f,indent=2);f.write('\n')
print(json.dumps(pin(out)))


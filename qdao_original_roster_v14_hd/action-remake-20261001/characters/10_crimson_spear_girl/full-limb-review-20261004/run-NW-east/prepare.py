from pathlib import Path
from PIL import Image
import json,hashlib
w=Path(__file__).parent;root=w.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in [2,3,5,6]:
 work=root/f'full-limb-review-20261004/run-NW/{n:02d}-v1'
 p=root/f'runtime/run/NW/{n:02d}.png';out=work/'edit-target-1254.png'
 Image.open(p).resize((1254,1254),Image.Resampling.LANCZOS).save(out)
 rec=Path(str(p)+'.generation.json')
 meta={'file':out.relative_to(root).as_posix(),'sha256':sha(out),'width':1254,'height':1254,'mode':'RGBA','operation':'Whole original1024 canvas resampled to1254; no translation/crop or pose change','derivedFrom':{'file':p.relative_to(root).as_posix(),'sha256':sha(p),'generationRecord':rec.relative_to(root).as_posix(),'recordSHA256':sha(rec)}}
 Path(str(out)+'.generation.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
 print(out)


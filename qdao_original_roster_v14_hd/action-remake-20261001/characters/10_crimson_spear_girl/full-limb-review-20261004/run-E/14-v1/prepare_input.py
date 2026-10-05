from pathlib import Path
from PIL import Image
import json,hashlib,datetime
w=Path(__file__).parent;root=w.parents[2]
p=root/'runtime/run/E/14.png';target=w/'edit-target-1254.png'
im=Image.open(p);im.resize((1254,1254),Image.Resampling.LANCZOS).save(target)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=Path(str(p)+'.generation.json')
meta={'file':target.relative_to(root).as_posix(),'sha256':sha(target),'width':1254,'height':1254,'mode':'RGBA','operation':'Whole original1024 RGBA canvas resampled to1254 before local editing; no translation/crop/bbox alignment/pose editing','derivedFrom':{'file':p.relative_to(root).as_posix(),'sha256':sha(p),'generationRecord':record.relative_to(root).as_posix(),'recordSHA256':sha(record)},'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
Path(str(target)+'.generation.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(json.dumps({'input':str(target),'sourceSHA':sha(p),'targetSHA':sha(target)}))


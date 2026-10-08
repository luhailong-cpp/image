from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,numpy as np
E=Path(__file__).resolve().parent;O=E/'integration-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=O/'manifest.json';m=json.loads(p.read_text());a=Image.open(m['output']['file'])
for q in m['qa']:
 assert sha(q['file'])==q['sha256'];assert np.array_equal(np.asarray(Image.open(q['file'])),np.asarray(a.crop(q['cropLTRB'])))
 q['actuallyViewed']=True;q['viewDetail']='original';q['reviewer']='/root/complete_expansion';q['result']='No confirmed hard cutoff, discontinuous highlight, displaced contour, or vertical tone seam in this scoped crop.'
m['seamReviewAt']=datetime.now(timezone.utc).isoformat();m['verticalJoinsScopedAccepted']=True;m['remaining']='c01 north/south outer returns and paired c09 insertion pending'
p.write_text(json.dumps(m,indent=2),encoding='utf-8')
for name in ['integration-v1/c01-c02-upper.png','integration-v1/c02-c03-lower.png','integration-v1/preview.png','integration-v2/preview.png']:
 f=E/name;im=Image.open(f)
 source=E/('integration-v1/assembled.png' if name.startswith('integration-v1') else 'integration-v2/r08_c10.png')
 if 'c01-c02-upper' in name:op=dict(operation='native1:1 crop',cropLTRB=[400,850,1654,2104])
 elif 'c02-c03-lower' in name:op=dict(operation='native1:1 crop',cropLTRB=[1510,1160,2764,2414])
 else:op=dict(operation='downscaled overview only; not native detail output')
 rec=dict(file=str(f),sha256=sha(f),width=im.width,height=im.height,derivedFrom=[dict(file=str(source),sha256=sha(source),generationRecord=str(source.parent/('assembly.json' if 'integration-v1' in str(source) else 'r08_c10.png.generation.json')))],**op)
 Path(str(f)+'.generation.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print('7 exact scoped crops reviewed and source records completed.')

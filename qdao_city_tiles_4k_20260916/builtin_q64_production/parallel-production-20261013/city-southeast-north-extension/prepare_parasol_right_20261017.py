from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).parent
s=B/'r12_c13/qa/repair-candidate-v04.png'
d=B/'r12_c13/repairs/parasol-right-20261017-v01'
d.mkdir(exist_ok=True)
o=d/'input.png';assert not o.exists()
Image.open(s).crop((1850,2500,3104,3754)).save(o)
(d/'coordinates.json').write_text(json.dumps({'source':str(s),'sourceSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'crop':[1850,2500,3104,3754],'input':str(o),'size':[1254,1254]},indent=2))

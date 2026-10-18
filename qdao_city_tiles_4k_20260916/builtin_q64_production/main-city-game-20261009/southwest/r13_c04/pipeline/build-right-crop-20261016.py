from pathlib import Path
from PIL import Image
import hashlib,json
T=Path(__file__).resolve().parents[1];s=T/'native/p01_04.png';p=T/'pipeline/guides/p01_03.right230-20261016-v02.png';assert not p.exists()
Image.open(s).crop((0,0,230,1254)).save(p)
d={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':str(s),'sourceSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'sourceCrop':[0,0,230,1254],'targetBox':[1024,0,1254,1254],'sourceResampling':False,'role':'exact real native right230 anchor only; provisional not passed QA','formalAccepted':False}
Path(str(p)+'.derivation.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(p)

from pathlib import Path
from PIL import Image
import hashlib,json
D=Path(__file__).parent
im=Image.open(D/'repair-v1/native.png').convert('RGBA');c=Image.open(D/'context.png').convert('RGBA');im.alpha_composite(c)
p=D/'repair-v2/hard-anchored-input.png';p.parent.mkdir(exist_ok=True);im.save(p)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(p.parent/'input-provenance.json').write_text(json.dumps({'file':str(p),'sha256':sha(p),'operation':'exact alpha composite native context over latest AI native; reference input only','sources':[{'file':str(q),'sha256':sha(q)} for q in [D/'repair-v1/native.png',D/'context.png']],'nativeScale':1,'guidePixels':False},indent=2))

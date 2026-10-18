from pathlib import Path
import hashlib,json
from PIL import Image
B=Path(__file__).parent
d=B/'r12_c14'
base=d/'qa/repair-candidate-v03.png'
patch=d/'repairs/lantern-middle-20261016-v01/native-v02.png'
out=d/'qa/repair-candidate-v09.png'
assert not out.exists()
im=Image.open(base).convert('RGB');p=Image.open(patch)
assert p.size==(1254,1254)
im.paste(p.crop((115,115,1139,1139)),(2560,2135))
im.save(out)
im.crop((2445,2020,3699,3274)).save(d/'qa/lantern-v09-local.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'candidate':str(out),'candidateSha256':sha(out),'size':[4096,4096],'base':str(base),'baseSha256':sha(base),'nativeRepair':str(patch),'nativeRepairSha256':sha(patch),'nativeSourceCrop':[115,115,1139,1139],'paste':[2560,2135],'resize':False,'status':'integration_review_pending','formalAccepted':False}
(d/'qa/repair-candidate-v09.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))


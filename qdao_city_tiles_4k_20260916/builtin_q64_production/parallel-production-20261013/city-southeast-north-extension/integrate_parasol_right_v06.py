from pathlib import Path
import hashlib,json
from PIL import Image
B=Path(__file__).parent
d=B/'r12_c13'
base=d/'qa/repair-candidate-v04.png'
patch=d/'repairs/parasol-right-20261017-v01/native-v01.png'
out=d/'qa/repair-candidate-v06.png'
assert not out.exists()
im=Image.open(base).convert('RGB');p=Image.open(patch)
assert p.size==(1254,1254)
im.paste(p.crop((115,115,1139,1139)),(1965,2615))
im.save(out)
im.crop((1850,2500,3104,3754)).save(d/'qa/parasol-right-v06-local.png')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'candidate':str(out),'candidateSha256':sha(out),'size':[4096,4096],'base':str(base),'baseSha256':sha(base),'nativeRepair':str(patch),'nativeRepairSha256':sha(patch),'nativeSourceCrop':[115,115,1139,1139],'paste':[1965,2615],'resize':False,'status':'integration_review_pending','formalAccepted':False}
(d/'qa/repair-candidate-v06.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))


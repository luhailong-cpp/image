import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).parent
d=B/'r12_c14/repairs/lantern-middle-20261016-v01'
s=Path('C:/Users/luyua/.codex/generated_images/01a1346c-f256-7660-bdc2-dd45a971f68b/exec-2dcc375b-f1b4-4ab1-9995-917cf465ac45.png')
out=d/'native-v02.png'
assert not out.exists()
shutil.copy2(s,out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'savedAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(s),'saved':str(out),'sha256':sha(out),'size':list(Image.open(out).size),'input':str(d/'input.png'),'inputSha256':sha(d/'input.png'),'entry':'image_gen__imagegen','actualModel':None,'coreContribution':0,'status':'native_repair_saved_integration_pending','visualReview':'Gold cap seam improved; lantern rib and horizontal ring geometry shifted. Integration pending.','formalAccepted':False,'toolCell':'lantern-second-call'}
(d/'native-v02.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))


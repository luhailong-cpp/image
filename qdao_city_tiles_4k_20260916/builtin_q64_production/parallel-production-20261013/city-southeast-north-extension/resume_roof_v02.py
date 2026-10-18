import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).parent
d=B/'r12_c14/repairs/roof-ridge-20261016-v01'
s=Path('C:/Users/luyua/.codex/generated_images/01a1346c-f256-7660-bdc2-dd45a971f68b/exec-327c6ff9-2337-46b0-bafb-5d075a73cb58.png')
out=d/'native-v02.png'
assert not out.exists()
shutil.copy2(s,out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'savedAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(s),'saved':str(out),'sha256':sha(out),'size':list(Image.open(out).size),'input':str(d/'input.png'),'inputSha256':sha(d/'input.png'),'entry':'image_gen__imagegen','actualModel':None,'coreContribution':0,'status':'native_repair_saved_integration_pending','visualReview':'Central roof seam improved, but tile row geometry changed outside narrow band. Integration perimeter must be checked.','formalAccepted':False,'toolCell':'roof-second-call'}
(d/'native-v02.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps(record))


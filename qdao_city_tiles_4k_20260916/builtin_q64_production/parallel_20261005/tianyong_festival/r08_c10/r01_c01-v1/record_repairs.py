from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
for version,hostfile in [('repair-v1','exec-8ae19b2c-9d76-4bcd-81d1-4d2b0c916a10.png'),('repair-v2','exec-3d8e1405-3490-43aa-9e2d-e8994436e2d6.png')]:
 d=P/version;host=Path('C:/Users/luyua/.codex/generated_images/01a11a14-aaa6-7b70-9759-64c9eb04ebff')/hostfile;dest=d/'native.png'
 if not dest.exists():shutil.copyfile(host,dest)
 assert sha(host)==sha(dest)
 req=json.loads((d/'request.json').read_text(encoding='utf-8-sig'))
 with Image.open(dest) as im:w,h=im.size;fmt=im.format;im.verify()
 record={'file':str(dest),'sha256':sha(dest),'generatedAt':None,'observedCompletionAt':datetime.now(timezone.utc).isoformat(),'width':w,'height':h,'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool exposes no model, quality, size selector and returns no verifiable backend model, quality or server generation time.','prompt':str(d/'prompt.txt'),'references':[ref(x) for x in req['payload']['referenced_image_paths']],'referenceRoles':req['referenceRoles'],'evidence':{'actualToolResponse':ref(d/'tool-response.json'),'actualRequest':ref(d/'request.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'candidateStatus':'unreviewed_native_return','countsAsComplete4KTile':False,'formalAccepted':False}
 (d/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'native':ref(dest),'pixels':[w,h]}))

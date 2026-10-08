from pathlib import Path
from PIL import Image
import json,hashlib,shutil,numpy as np
O=Path(__file__).resolve().parent
host=Path(r'C:/Users/luyua/.codex/generated_images/01a11a13-683c-7411-9506-ef923388db00/exec-6de16103-3a7c-4991-b682-a8190222f63e.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
shutil.copyfile(host,O/'native.png')
req=json.loads((O/'request.json').read_text(encoding='utf-8'));rec=json.loads((O/'tool-response.json').read_text(encoding='utf-8'))
with Image.open(O/'native.png') as im:w,h=im.size
record={'file':str(O/'native.png'),'sha256':sha(O/'native.png'),'generatedAt':None,'observedCompletionAt':rec['observedCompletionAt'],'width':w,'height':h,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; no model/quality/size selector and no verifiable backend model or quality returned.','prompt':str(O/'prompt.txt'),'references':req['references'],'referenceRoles':req['referenceRoles'],'evidence':{'toolResponse':info(O/'tool-response.json'),'request':info(O/'request.json'),'hostSavedOutput':info(host),'copiedByteIdentically':sha(host)==sha(O/'native.png')},'formalAccepted':False}
(O/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
base=Image.open(O.parent/'final-registration-v1/joined.png')
for name,image in [('base',base),('new',Image.open(O/'native.png'))]:image.crop((150,0,700,400)).save(O/(name+'-upper.png'))



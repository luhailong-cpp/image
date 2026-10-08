from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil,sys
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
host=Path(sys.argv[1]);dest=P/'native.png'
assert not dest.exists();shutil.copyfile(host,dest)
assert sha(host)==sha(dest)
request=json.loads((P/'request.json').read_text(encoding='utf-8-sig'));prep=json.loads((P/'preparation.json').read_text(encoding='utf-8-sig'))
with Image.open(dest) as im:w,h=im.size;fmt=im.format;im.verify()
record={'file':str(dest),'sha256':sha(dest),'generatedAt':None,'observedCompletionAt':datetime.now(timezone.utc).isoformat(),'width':w,'height':h,'format':fmt,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':request['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool exposes no model, quality, size selector and returns no verifiable backend model, quality or generation timestamp.','prompt':str(P/'prompt.txt'),'references':prep['references'],'referenceRoles':request['referenceRoles'],'evidence':{'actualToolResponse':ref(P/'tool-response.json'),'actualRequest':ref(P/'request.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'candidateStatus':'unreviewed_native_return','countsAsComplete4KTile':False,'formalAccepted':False}
(P/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native':ref(dest),'pixels':[w,h]}))

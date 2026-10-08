from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
from datetime import datetime,timezone
D=Path(__file__).parent;P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
req=json.loads((D/'request.json').read_text(encoding='utf-8'))
host=Path(r'C:/Users/luyua/.codex/generated_images/01a11b00-53b8-70a3-bc9b-96606ec052ee/exec-95dab7e0-d59b-4d1b-a0ef-77abdf2f9b52.png')
im=Image.open(D/'native.png')
assert im.size==(1254,1254) and sha(host)==sha(D/'native.png')
rec={'operation':'builtin AI local surface repair','tool':'image_gen.imagegen','route':'builtin','file':str(D/'native.png'),'sha256':sha(D/'native.png'),'generatedAt':None,'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'nativeWidth':1254,'nativeHeight':1254,'format':'PNG','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in tool exposes no model/quality selectors and did not disclose actual model, quality or generation time. Configuration targets and prompt are not actual backend evidence.','hostSource':info(host),'evidence':info(D/'tool-response.json'),'prompt':info(D/'prompt.txt'),'references':req['references'],'editedFrom':req['source'],'nativeScale':1,'formalAccepted':False}
(D/'native.png.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
original=np.array(Image.open(req['source']['file']).convert('RGB'))
new=np.array(im.convert('RGB'))
for x in [510,550,600,650,700,750,800,850]:
 y=int(np.argmax(original[500:780,x].mean(1))+500)
 print(x,y,original[y,x].tolist())

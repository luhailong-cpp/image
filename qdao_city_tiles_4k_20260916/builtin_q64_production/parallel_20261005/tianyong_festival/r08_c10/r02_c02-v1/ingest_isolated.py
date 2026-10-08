from pathlib import Path
from PIL import Image
import json,hashlib,shutil,numpy as np
O=Path(__file__).resolve().parent;T=O.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
host=Path(r'C:/Users/luyua/.codex/generated_images/01a11a13-683c-7411-9506-ef923388db00/exec-807ac9c6-d125-4681-8ac1-bc02b885db91.png')
assert not (O/'native.png').exists();shutil.copyfile(host,O/'native.png')
req=json.loads((O/'request.json').read_text(encoding='utf-8'));prep=json.loads((O/'preparation.json').read_text(encoding='utf-8'));rec=json.loads((O/'tool-response.json').read_text(encoding='utf-8'))
n=np.array(Image.open(O/'native.png').convert('RGB'));assert n.shape==(1254,1254,3)
record={'file':str(O/'native.png'),'sha256':sha(O/'native.png'),'generatedAt':None,'observedCompletionAt':rec['observedCompletionAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Hostmanaged; no model/quality/size selectors or verifiablebackendfields returned','prompt':str(O/'prompt.txt'),'references':prep['references'],'referenceRoles':['edit target exact native top/bottomcontext','canonical layout only; pixelsnotfinal','approvedprimarypaintingstyle'],'evidence':{'toolResponse':info(O/'tool-response.json'),'request':info(O/'request.json'),'hostOutput':info(host),'copiedByteIdentically':sha(host)==sha(O/'native.png')},'formalAccepted':False}
(O/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'))
c=np.array(Image.open(cp['fragment']['file']).convert('RGBA').crop((909,909,2163,2163)))
Image.fromarray(c).save(O/'context-latest.png')
j=n.copy();j[c[:,:,3]==255]=c[:,:,:3][c[:,:,3]==255];Image.fromarray(j).save(O/'naive-latest.png')
Image.fromarray(j).crop((0,780,1254,1254)).save(O/'lower-comparison.png')
print(cp['version'])


from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,shutil
from PIL import Image
D=Path(__file__).parent;src=Path(sys.argv[1]);dest=D/(sys.argv[2] if len(sys.argv)>2 else 'native.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((D/'request.json').read_text(encoding='utf-8-sig'));prep=json.loads((D/'preparation.json').read_text(encoding='utf-8-sig'))
shutil.copy2(src,dest)
with Image.open(dest) as im:sz=im.size;fmt=im.format
assert sz==(1254,1254)
record={'file':str(dest),'sha256':sha(dest),'generatedAt':None,'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'native':{'width':sz[0],'height':sz[1],'format':fmt},'tool':'image_gen.imagegen','route':'builtin','toolResultId':src.stem,'sourceFile':{'file':str(src),'sha256':sha(src)},'configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实元数据；提示词与项目配置不代表显式锁定。','prompt':str(D/'prompt.txt'),'references':prep['references'],'evidence':{'file':str(D/'tool-response.json')},'nativeScale':1,'noUpscale':True,'formalAccepted':False}
if dest.parent!=D:
 request=json.loads((dest.parent/'request.json').read_text(encoding='utf-8'))
 record['prompt']=str(dest.parent/'prompt.txt')
 record['references']=[{'file':p,'sha256':sha(p)} for p in request['referenced_image_paths']]
 record['evidence']={'file':str(dest.parent/'tool-response.json')}
 record['operation']='builtin AI edit correcting erroneous lower-left inset material and removing false horizontal joint'
Path(str(dest)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dest),'sha256':sha(dest),'pixels':sz}))

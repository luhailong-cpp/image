from pathlib import Path
from PIL import Image
import json,hashlib,shutil
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c03-v2/left-lower-repair-v1')
host=Path(r'C:/Users/luyua/.codex/generated_images/01a11ac0-9b70-7362-b220-9b7f91951d42/exec-92bcba8c-d7df-4884-88de-27f15216ef88.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
shutil.copyfile(host,D/'native.png')
req=json.loads((D/'request.json').read_text(encoding='utf-8'));rec=json.loads((D/'tool-response.json').read_text(encoding='utf-8'))
record={'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'generatedAt':None,'observedCompletionAt':rec['observedCompletionAt'],'pixels':list(Image.open(D/'native.png').size),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; selectors and verified backend fields not returned','prompt':str(D/'prompt.txt'),'references':req['references'],'evidence':{'toolResponse':info(D/'tool-response.json'),'request':info(D/'request.json'),'hostOutput':info(host),'copiedByteIdentically':sha(host)==sha(D/'native.png')},'formalAccepted':False}
(D/'native.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(info(D/'native.png')))




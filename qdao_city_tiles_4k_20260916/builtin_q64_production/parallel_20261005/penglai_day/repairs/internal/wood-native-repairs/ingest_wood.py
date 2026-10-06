from pathlib import Path
from PIL import Image
import json,hashlib,datetime,shutil,re
D=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,r):Path(p).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
for n in ['wood2048','wood3072']:
 ev=read(D/(n+'-tool-result.json'))
 src=Path(re.search(r'as (C:.*?\.png) by default',ev['output_hint']).group(1))
 dst=D/(n+'-native.png');shutil.copy2(src,dst)
 refs=[D/(n+'-context1254.png'),Path('D:/work/image/designs/gameplay-ui/04-guild.png')]
 rec={'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'generatedAtEvidence':'Local tool output file modification time; service timestamp not exposed','width':Image.open(dst).width,'height':Image.open(dst).height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','toolResultPath':str(src),'configSnapshot':read('D:/work/image/config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'prompt':(D/(n+'.prompt.txt')).read_text(encoding='utf-8'),'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed built-in tool exposes no model or quality selectors or returned actual values. Prompt and configuration are not proof of actual model/quality.','promptFile':str(D/(n+'.prompt.txt')),'references':[{'file':str(p),'sha256':sha(p),'role':'exact edit target' if i==0 else 'approved style only'} for i,p in enumerate(refs)],'role':'native wood material seam repair','evidence':ev,'formalAccepted':False}
 write(str(dst)+'.generation.json',rec)
 print(n,Image.open(dst).size,sha(dst))


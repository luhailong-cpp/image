from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;O=D/'join-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Path('C:/Users/luyua/.codex/generated_images/01a10bad-0c92-7f93-8a5b-4ae4ec120204/exec-599bb307-6db9-44f2-82a2-cd35e8162d9a.png');assert not (D/'native.png').exists();shutil.copy2(src,D/'native.png')
req=read(D/'request.json');prep=read(D/'preparation.json');A=np.asarray(Image.open(D/'native.png').convert('RGB'));K=np.asarray(Image.open(D/'context.png').convert('RGBA'));assert A.shape==(1254,1254,3)
save(D/'native.png.generation.json',{'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'generatedAt':None,'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool does not disclose version or quality; no verifiable metadata provided','evidence':[ref(D/'tool-receipt.json'),ref(src)],'prompt':str(D/'prompt.txt'),'references':prep['references'],'nativeScale':1,'formalAccepted':False})
O.mkdir(exist_ok=False)
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
x=np.arange(1254)[None,:];y=np.arange(1254)[:,None];w=smooth((x-54)/61)*smooth((y-54)/61)
J=np.rint(A*w[:,:,None]+K[:,:,:3]*(1-w[:,:,None])).astype(np.uint8);assert np.array_equal(J[115:,115:],A[115:,115:]);assert np.array_equal(J[:54,:],K[:54,:,:3]) and np.array_equal(J[:,:54],K[:,:54,:3]);Image.fromarray(J).save(O/'joined.png');Image.fromarray(np.rint(w*255).astype(np.uint8)).save(O/'native-weight.png')
canvas=Image.new('RGBA',(1454,1454),(0,0,0,0));cx,cy=40960-315,28672-315
for tile,v in prep['sources'].items():
 assert sha(v['file'])==v['sha256'];ox,oy=(int(tile[5:7])-1)*4096,(int(tile[1:3])-1)*4096;im=Image.open(v['file']).convert('RGBA');canvas.paste(im,(ox-cx,oy-cy))
canvas.paste(Image.fromarray(J),(200,200));canvas.crop((0,0,1454,640)).save(O/'top-native-qa.png');canvas.crop((0,0,640,1454)).save(O/'left-native-qa.png');canvas.crop((0,0,640,640)).save(O/'corner-native-qa.png')
assembly={'output':ref(O/'joined.png'),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'nativeScale':1,'registrationApplied':False,'toneCorrectionApplied':False,'resized':False,'operation':'Native 1:1 composition. Smoothstep native weight within known top/left return strips54..115. All previously missing pixels equal the generated output exactly.','nativeWeight':ref(O/'native-weight.png'),'visualReviewPending':True,'formalAccepted':False,'qa':{'worldTopLeft':[cx,cy],'joinedAt':[200,200],'nativeScale':1,'sources':list(prep['sources'].values())}}
save(O/'assembly.json',assembly);save(O/'joined.png.generation.json',{'file':str(O/'joined.png'),'sha256':sha(O/'joined.png'),'operation':'Exact native composition; no resize or generation','derivedFrom':[ref(D/'native.png'),ref(D/'context.png')],'assembly':ref(O/'assembly.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False})
print(json.dumps({'joined':ref(O/'joined.png')}))

from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Path('C:/Users/luyua/.codex/generated_images/01a10bad-0c92-7f93-8a5b-4ae4ec120204/exec-7813cf1b-daee-42d8-96b1-ece1072eeb44.png')
if not (D/'native.png').exists():shutil.copy2(src,D/'native.png')
req=read(D/'request.json');prep=read(D/'preparation.json');N=np.asarray(Image.open(D/'native.png').convert('RGB'));K=np.asarray(Image.open(D/'context.png').convert('RGBA'));assert N.shape==(1254,1254,3)
save(D/'native.png.generation.json',{'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'generatedAt':None,'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; tool does not disclose model or quality, nor supply verifiable metadata','evidence':[ref(D/'tool-receipt.json'),ref(src)],'prompt':str(D/'prompt.txt'),'references':prep['references'],'nativeScale':1,'formalAccepted':False})
O=D/'join-v1';O.mkdir(exist_ok=False)
x=np.arange(1254)[None,:];y=np.arange(1254)[:,None]
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
w=np.broadcast_to(smooth((x-54)/61),(1254,1254)).copy();w[:,:115]*=(1-smooth((y-1139)/61));w[:,115:]=1
joined=np.rint(N*w[:,:,None]+K[:,:,:3]*(1-w[:,:,None])).astype(np.uint8)
assert np.array_equal(joined[:,:54],K[:,:54,:3]);assert np.array_equal(joined[:,115:],N[:,115:])
Image.fromarray(joined).save(O/'joined.png');Image.fromarray(np.rint(w*255).astype(np.uint8)).save(O/'native-weight.png')
L=Image.open(prep['sources']['r07_c10']['file']).convert('RGB');B=Image.open(prep['sources']['r08_c10']['file']).convert('RGB')
Q=Image.new('RGB',(640,1400));Q.paste(L.crop((3781,2857,4096,4096)),(0,0));Q.paste(B.crop((3781,0,4096,161)),(0,1239));Q.paste(Image.fromarray(joined).crop((0,0,440,1254)),(200,100));Q.save(O/'left-seam-native-qa.png')
Image.fromarray(joined).crop((0,1000,500,1254)).save(O/'corner-native-qa.png')
save(O/'assembly.json',{'output':ref(O/'joined.png'),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'nativeScale':1,'registrationApplied':False,'toneCorrectionApplied':False,'resized':False,'operation':'Native 1:1 composition, left115 known strip only; smoothstep within left return x54..115 and bottom-corner y1139..1200; missing pixels remain original generated pixels.','nativeWeight':ref(O/'native-weight.png'),'visualReviewPending':True,'formalAccepted':False})
save(O/'joined.png.generation.json',{'file':str(O/'joined.png'),'sha256':sha(O/'joined.png'),'operation':'Exact-size native composition, no generation or resizing','derivedFrom':[ref(D/'native.png'),ref(D/'context.png')],'assembly':ref(O/'assembly.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False})
print(json.dumps({'joined':ref(O/'joined.png'),'qa':str(O/'left-seam-native-qa.png')}))

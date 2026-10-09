from pathlib import Path
from datetime import datetime, timezone
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent
D=N/sys.argv[1]; src=Path(sys.argv[2]); O=D/'join-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
req=read(D/'request.json'); prep=read(D/'preparation.json'); r=req['row'];c=req['col']; box=req['tileLocalCropLTRB'];x0,y0=box[:2]
assert src.exists(); shutil.copy2(src,D/'native.png')
save(D/'tool-receipt.json',{'tool':'image_gen.imagegen','outputHintNativeFile':str(src),'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'actualModel':None,'actualQuality':None,'submittedParameters':req['submittedParameters']})
save(D/'native.png.generation.json',{'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'generatedAt':None,'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; exact model and quality are not disclosed or selectable in this tool.','evidence':[ref(D/'tool-receipt.json'),ref(src)],'prompt':req['payload']['prompt'],'references':prep['references'],'nativeScale':1,'formalAccepted':False})
native=np.asarray(Image.open(D/'native.png').convert('RGB'));known=np.asarray(Image.open(D/'context.png').convert('RGBA'));assert native.shape==(1254,1254,3)
assert not (O/'manifest.json').exists(),'Cannot rebuild a published manifest directory'
O.mkdir(exist_ok=True)
x=np.arange(1254)[None,:];y=np.arange(1254)[:,None]
def smooth(a):a=np.clip(a,0,1);return a*a*(3-2*a)
left=115 if c==1 else 230
w=np.broadcast_to(smooth((x-54)/(left-54)),(1254,1254)).copy()
if r<4:w*=1-smooth((y-1024)/176)
elif prep.get('contextNeighbors'):w*=1-smooth((y-1139)/61)
w[known[:,:,3]==0]=1
joined=np.rint(native*w[:,:,None]+known[:,:,:3]*(1-w[:,:,None])).astype(np.uint8)
assert np.array_equal(joined[known[:,:,3]==0],native[known[:,:,3]==0])
J=Image.fromarray(joined);J.save(O/'joined.png');Image.fromarray(np.rint(w*255).astype(np.uint8)).save(O/'native-weight.png')
# Build a 1:1 neighborhood around the actual placement. It includes real pixels outside the edited window.
F=Image.open(prep['sources']['fragment']['file']).convert('RGBA'); L=Image.open(prep['sources']['left']['file']).convert('RGBA');B=Image.open(prep['sources']['belowLeft']['file']).convert('RGBA')
world=Image.new('RGBA',(5350,5350))
# Neighborhood origin in current-tile coordinates is (-115,-115). Outside unavailable regions stay transparent.
world.paste(L.crop((3981,0,4096,4096)),(0,115));world.paste(B.crop((3981,0,4096,1139)),(0,4211));world.alpha_composite(F,(115,115))
for neighbor in prep.get('contextNeighbors',[]):
 im=Image.open(neighbor['file']).convert('RGBA');b=neighbor['relativeTileLTRB'];world.alpha_composite(im.crop((0,0,4096,min(4096,5235-b[1]))),(b[0]+115,b[1]+115))
world.paste(J.convert('RGBA'),(x0+115,y0+115))
qa=[]
leftq=(max(-115,x0-100),max(-115,y0-70),min(4096,x0+500),min(4211,y0+1324))
q=world.crop(tuple(v+115 for v in leftq));q.save(O/'left-placement-native-qa.png');qa.append({'file':str(O/'left-placement-native-qa.png'),'tileLocalLTRB':list(leftq)})
if r<4:
 bq=(max(-115,x0),y0+900,min(4096,x0+1254),min(4096,y0+1370));q=world.crop(tuple(v+115 for v in bq));q.save(O/'bottom-placement-native-qa.png');qa.append({'file':str(O/'bottom-placement-native-qa.png'),'tileLocalLTRB':list(bq)})
elif prep.get('contextNeighbors'):
 bq=(max(-115,x0-100),3935,min(4096,x0+1254),4296);q=world.crop(tuple(v+115 for v in bq));q.save(O/'bottom-placement-native-qa.png');qa.append({'file':str(O/'bottom-placement-native-qa.png'),'tileLocalLTRB':list(bq)})
save(O/'qa-index.json',{'nativeScale':1,'images':[ref(O/'joined.png')]+[{**ref(a['file']),'tileLocalLTRB':a['tileLocalLTRB']} for a in qa]})
save(O/'assembly.json',{'output':ref(O/'joined.png'),'native':ref(D/'native.png'),'context':ref(D/'context.png'),'nativeScale':1,'registrationApplied':False,'toneCorrectionApplied':False,'resized':False,'operation':f'Native 1:1 composition. Known left weight transitions x54..{left}; '+('known bottom y1024..1200. ' if r<4 else '')+'Unknown pixels remain exact generated pixels. No geometric resampling, blur or color correction.','nativeWeight':ref(O/'native-weight.png'),'visualReviewPending':True,'formalAccepted':False})
save(O/'joined.png.generation.json',{'file':str(O/'joined.png'),'sha256':sha(O/'joined.png'),'operation':'Exact-size native composition, no generation or resizing','derivedFrom':[ref(D/'native.png'),ref(D/'context.png')],'assembly':ref(O/'assembly.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False})
print(json.dumps({'joined':ref(O/'joined.png'),'qa':read(O/'qa-index.json')}))

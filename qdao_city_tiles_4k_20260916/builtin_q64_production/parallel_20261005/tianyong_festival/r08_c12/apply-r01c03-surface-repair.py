from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;D=N/'r01_c03-v1';O=D/'join-v1';R=D/'surface-repair-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
host=Path(r'C:/Users/luyua/.codex/generated_images/01a11b00-53b8-70a3-bc9b-96606ec052ee/exec-5a5be8db-73e3-4821-b9ff-4d8087de3a22.png')
assert sha(R/'before.png')=='2d574dc6d95016804ce1ba8be1d98f60555bb425312feefbad0fc2e30bb6602a'
B=np.array(Image.open(R/'before.png').convert('RGB'));A=np.array(Image.open(R/'native.png').convert('RGB'));assert A.shape==B.shape==(1254,1254,3)
x=np.arange(1254)[None,:];y=np.arange(1254)[:,None];l,t,r,b=54,325,1127,483
def sm(v):v=np.clip(v,0,1);return v*v*(3-2*v)
w=sm((x-l)/8)*sm((r-1-x)/8)*sm((y-t)/8)*sm((b-1-y)/8)
J=np.rint(A*w[:,:,None]+B*(1-w[:,:,None])).astype(np.uint8);change=np.any(J!=B,axis=2)
assert np.array_equal(J[w==0],B[w==0])
Image.fromarray(J).save(O/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(R/'native-weight.png');Image.fromarray((change*255).astype('uint8')).save(R/'changed-pixels-mask.png')
Image.fromarray(J).crop((0,300,1180,535)).save(R/'after-closeup-native.png')
stamp=datetime.now(timezone.utc).isoformat();req=read(D/'request.json')
save(R/'native.png.generation.json',{'file':str(R/'native.png'),'sha256':sha(R/'native.png'),'hostOutput':ref(host),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None,'actualSizeParameter':None,'request':ref(R/'request.json'),'observedCompletionAtUtc':stamp,'pixels':[1254,1254],'nativeScale':1,'formalAccepted':False})
proof={'before':ref(R/'before.png'),'repairNative':ref(R/'native.png'),'after':ref(O/'joined.png'),'roiLTRB':[l,t,r,b],'nativeWeight':ref(R/'native-weight.png'),'changedMask':ref(R/'changed-pixels-mask.png'),'changedPixels':int(change.sum()),'allPixelsOutsideWeightIdentical':True,'operation':'Native pixel composition with an 8-pixel smoothstep at explicit ROI boundaries; no image blur, warp, resizing, tone correction, or imported guide pixels. Pixels outside ROI remain exact.','actualModel':None,'actualQuality':None,'generationRecord':ref(R/'native.png.generation.json'),'nativeScale':1,'formalAccepted':False}
save(R/'source-proof.json',proof)
assembly=read(O/'assembly.json');assembly['output']=ref(O/'joined.png');assembly['surfaceRepair']=ref(R/'source-proof.json');assembly['operation']+=' One documented local AI surface repair is then applied only in its explicit ROI.';save(O/'assembly.json',assembly)
gen=read(O/'joined.png.generation.json');gen['sha256']=sha(O/'joined.png');gen['derivedFrom']=[ref(R/'before.png'),ref(R/'native.png')];gen['assembly']=ref(O/'assembly.json');gen['localAIRepair']=ref(R/'source-proof.json');save(O/'joined.png.generation.json',gen)
prep=read(D/'preparation.json');world=req['globalCropLTRB'];cx,cy=world[0]-200,world[1]-200;canvas=Image.new('RGBA',(1654,1654))
for tile,v in prep['sources'].items():
 assert sha(v['file'])==v['sha256'];ox=(int(tile[5:7])-1)*4096;oy=(int(tile[1:3])-1)*4096;canvas.alpha_composite(Image.open(v['file']).convert('RGBA'),(ox-cx,oy-cy))
canvas.paste(Image.fromarray(J),(200,200));canvas.crop((0,0,1654,660)).save(O/'top-native-qa.png');canvas.crop((0,0,660,1654)).save(O/'left-native-qa.png')
print(json.dumps({'joined':ref(O/'joined.png'),'proof':ref(R/'source-proof.json'),'changed':int(change.sum())}))


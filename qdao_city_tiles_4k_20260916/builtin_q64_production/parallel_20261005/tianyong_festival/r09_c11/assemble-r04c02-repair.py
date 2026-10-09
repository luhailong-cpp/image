from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent
D=N/'r04_c02-v1'; R=D/'base-repair-v1'; O=D/'join-v2'; O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
src=Path(r'C:\Users\luyua\.codex\generated_images\01a10bad-0c92-7f93-8a5b-4ae4ec120204\exec-70b211ad-c8f4-4247-a582-7ba7c930071d.png')
shutil.copy2(src,R/'native.png')
B=np.asarray(Image.open(D/'join-v1/joined.png').convert('RGB')); A=np.asarray(Image.open(R/'native.png').convert('RGB')); assert A.shape==B.shape==(1254,1254,3)
box=[480,700,1254,1254];l,t,r,b=box
y,x=np.mgrid[0:1254,0:1254]; w=np.clip(np.minimum.reduce([(x-l)/12,(y-t)/12]),0,1); w=w*w*(3-2*w)
J=np.rint(A*w[:,:,None]+B*(1-w[:,:,None])).astype(np.uint8); assert np.array_equal(J[w==0],B[w==0])
Image.fromarray(J).save(O/'joined.png');Image.fromarray(np.rint(w*255).astype(np.uint8)).save(O/'repair-native-weight.png')
prep=read(D/'preparation.json');req=read(D/'request.json');world=req['globalCropLTRB']
canvas=Image.new('RGBA',(1654,1654));cx,cy=world[0]-200,world[1]-200
for name,v in prep['sources'].items():
 assert sha(v['file'])==v['sha256'];ox=(int(name[5:7])-1)*4096;oy=(int(name[1:3])-1)*4096;canvas.alpha_composite(Image.open(v['file']).convert('RGBA'),(ox-cx,oy-cy))
canvas.paste(Image.fromarray(J),(200,200));canvas.crop((0,0,1654,660)).save(O/'top-native-qa.png');canvas.crop((0,0,660,1654)).save(O/'left-native-qa.png')
save(R/'native.png.generation.json',{'file':str(R/'native.png'),'sha256':sha(R/'native.png'),'pixels':[1254,1254],'tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],'submittedParameters':req['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes neither model nor quality selectors or returned identifiers','evidence':[ref(R/'tool-receipt.json'),ref(src),ref(R/'request.json')],'references':[ref(Path(p)) for p in read(R/'request.json')['payload']['referenced_image_paths']],'observedCompletionAtUtc':read(R/'tool-receipt.json')['observedAtUtc'],'nativeScale':1,'formalAccepted':False})
save(O/'assembly.json',{'output':ref(O/'joined.png'),'baseAssembly':ref(D/'join-v1/assembly.json'),'baseJoined':ref(D/'join-v1/joined.png'),'nativeRepair':ref(R/'native.png'),'repairGeneration':ref(R/'native.png.generation.json'),'repairWeight':ref(O/'repair-native-weight.png'),'repairROI':box,'maskTransitionPixels':12,'maskEdges':'12px left/top transition; native reaches right/bottom image edges to remove invented curb entirely','nativeScale':1,'registrationApplied':False,'toneCorrectionApplied':False,'resized':False,'changedPixels':int(np.any(J!=B,axis=2).sum()),'outsideROIPreservedExactly':True,'operation':'Genuine AI repair native pixels in explicit local ROI only; 12px smoothstep left/top perimeter, no geometry remap, no painted synthetic lines; original joined pixels unchanged elsewhere.','visualReviewPending':True,'formalAccepted':False,'qa':{'worldTopLeft':[cx,cy],'joinedAt':[200,200],'nativeScale':1,'sources':list(prep['sources'].values())}})
save(O/'joined.png.generation.json',{'file':str(O/'joined.png'),'sha256':sha(O/'joined.png'),'operation':'Native composition plus explicit genuine AI repair ROI; no resize','derivedFrom':[ref(D/'join-v1/joined.png'),ref(R/'native.png')],'generationRecords':[ref(D/'native.png.generation.json'),ref(R/'native.png.generation.json')],'assembly':ref(O/'assembly.json'),'newModelCalls':0,'upstreamAdditionalModelCalls':1,'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False})
print(json.dumps(ref(O/'joined.png')))

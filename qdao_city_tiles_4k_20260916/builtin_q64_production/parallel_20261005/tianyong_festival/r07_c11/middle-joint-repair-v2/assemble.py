from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent;N=D.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=read(D/'request.json');host=Path('C:/Users/luyua/.codex/generated_images/01a11b00-53b8-70a3-bc9b-96606ec052ee/exec-81f179bb-1dad-4a71-804f-266366c7b456.png');shutil.copyfile(host,D/'native.png');G=Image.open(D/'native.png').convert('RGBA');assert G.size==(1254,1254)
save(D/'native.png.generation.json',{'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'tool':'image_gen.imagegen','route':'builtin','observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'configSnapshot':q['configSnapshot'],'submittedParameters':q['submittedParameters'],'actualModel':None,'actualQuality':None,'actualPixels':list(G.size),'unverifiedReason':'Host does not expose or accept model/quality/size fields.','sourceHostImage':ref(host),'request':ref(D/'request.json'),'prompt':q['payload']['prompt'],'references':q['references'],'nativeScale':1,'formalAccepted':False})
B=np.array(Image.open(D/'original-context.png').convert('RGBA'));g=np.asarray(G);mask=np.zeros((1254,1254),np.uint8);mask[535:905,445:865]=1;mask[765:905,215:445]=1
dist=np.zeros(mask.shape,np.float32);inner=mask.astype(bool)
for step in range(13):
 dist+=inner;inner=inner & np.roll(inner,1,0) & np.roll(inner,-1,0) & np.roll(inner,1,1) & np.roll(inner,-1,1)
z=np.clip((dist-1)/12,0,1);w=z*z*(3-2*z);J=np.rint(B.astype(float)*(1-w[:,:,None])+g.astype(float)*w[:,:,None]).astype(np.uint8)
assert np.array_equal(J[mask==0],B[mask==0]);Image.fromarray(J).save(D/'joined.png');Image.fromarray(np.uint8(np.rint(w*255))).save(D/'applied-weight-mask.png')
box=q['windowTileLocalLTRB'];roi=[1400,1770,2050,2140];local=[roi[0]-box[0],roi[1]-box[1],roi[2]-box[0],roi[3]-box[1]];Image.fromarray(J).crop(local).save(D/'repair.png')
S=Image.open(q['source']['file']).convert('RGBA');before=np.array(S);S.paste(Image.open(D/'repair.png'),tuple(roi[:2]));after=np.asarray(S);changed=np.any(before!=after,axis=2);outside=changed.copy();outside[roi[1]:roi[3],roi[0]:roi[2]]=False;assert not outside.any();S.crop((1250,1660,2210,2230)).save(D/'after-closeup-native.png')
proof={'source':q['source'],'native':ref(D/'native.png'),'joined':ref(D/'joined.png'),'windowTileLocalLTRB':box,'repairTileLocalLTRB':roi,'changedPixels':int(changed.sum()),'unchangedOutsideRepairRoi':True,'actualMaskSource':ref(D/'applied-weight-mask.png'),'maskPartsTileLocalLTRB':[[1630,1770,2050,2140],[1400,2000,1630,2140]],'maskReason':'Native tool bends the incoming joint slightly before the original hole; explicit left corridor includes the true generated junction and prevents cutting the repaired groove mid-curve. Upper-left area stays exact original.','operation':'Native1:1 generated crop composition with12pixel smoothstep weight inside explicit mask only; no pixel blur, resize, warp or tone correction.','newModelCalls':0,'actualModel':None,'actualQuality':None,'visualReviewPending':True,'formalAccepted':False};save(D/'source-proof.json',proof)
for name in ['joined.png','repair.png','after-closeup-native.png']:
 save(D/(name+'.generation.json'),{'file':str(D/name),'sha256':sha(D/name),'derivedFrom':[q['source'],ref(D/'native.png')],'operation':proof['operation'],'sourceProof':ref(D/'source-proof.json'),'nativeScale':1,'newModelCalls':0,'formalAccepted':False})
print(json.dumps({'joined':ref(D/'joined.png'),'repair':ref(D/'repair.png'),'proof':ref(D/'source-proof.json'),'changedPixels':int(changed.sum())}))

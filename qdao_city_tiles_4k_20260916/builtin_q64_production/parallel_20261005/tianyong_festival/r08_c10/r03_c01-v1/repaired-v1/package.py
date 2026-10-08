from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent;O=P/'registration-v1';R=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
prep=read(R/'preparation.json');inputs={p['tile']:p for p in prep['nativeInputs']}
for i in inputs.values():assert sha(i['file'])==i['sha256']
joined=Image.open(O/'joined.png').convert('RGB');arr=np.array(joined)
ctx=np.array(Image.open(P/'original-context.png').convert('RGBA'));known=ctx[:,:,3]==255
assert np.count_nonzero(~known)==930816
specs=[
 ('new-placement.png','r08_c10',[115,0,1024,1024],[0,1933,909,2957],None),
 ('left-return-placement.png','r08_c09',[12,12,115,1226],[3993,1945,4096,3159],inputs['r08_c09']),
 ('right-return-placement.png','r08_c10',[1024,12,1226,1226],[909,1945,1111,3159],inputs['r08_c10']),
 ('bottom-return-placement.png','r08_c10',[115,1024,1024,1226],[0,2957,909,3159],inputs['r08_c10'])]
patches=[];mask=np.zeros(known.shape,bool)
for n,tile,crop,dst,prior in specs:
 joined.crop(crop).save(O/n);mask[crop[1]:crop[3],crop[0]:crop[2]]=True
 patches.append({'asset':info(O/n),'cropFromJoinedLTRB':crop,'destinationTile':tile,'destinationTileLTRB':dst,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
 save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(O/'joined.png')],'operation':'Exact native crop, no resize','cropLTRB':crop,'newModelCalls':0,'nativeScale':1})
assert np.array_equal(arr[known&~mask],ctx[:,:,:3][known&~mask])
save('patches-draft.json',{'joined':info(O/'joined.png'),'windowTileLocalLTRB':[-115,1933,1139,3187],'windowGlobalLTRB':[36749,30605,38003,31859],'patches':patches,'nativeScale':1,'formalAccepted':False})
# Native surrounding-source montage, same world pixels, preview in task directory only.
canvas=Image.new('RGBA',(1454,1454))
for tile,ref in inputs.items():
 im=Image.open(ref['file']).convert('RGBA')
 if tile=='r08_c09': offset=(-3881,-1833)
 else: offset=(215,-1833)
 canvas.paste(im,offset)
canvas.paste(joined,(100,100));canvas.save(O/'surrounding-native.png')
save('surrounding-native.png.generation.json',{**info(O/'surrounding-native.png'),'derivedFrom':[info(O/'joined.png')]+list(inputs.values()),'operation':'Native 1:1 composed candidate with surrounding source pixels; transparent still missing','newModelCalls':0})
for n,b in [('outer-left.png',[0,0,380,1454]),('outer-right.png',[1080,0,1454,1454]),('outer-bottom.png',[0,1060,1454,1454]),('outer-top-known-corners.png',[0,0,1454,230])]:
 canvas.crop(b).save(O/n);save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(O/'surrounding-native.png')],'operation':'Exact native crop for exterior edge inspection','cropLTRB':b,'newModelCalls':0})
print(json.dumps({'joined':info(O/'joined.png'),'newNativePixels':930816,'untouchedKnownPixelsOutsideManifest':int((known&~mask).sum()),'patches':len(patches)}))

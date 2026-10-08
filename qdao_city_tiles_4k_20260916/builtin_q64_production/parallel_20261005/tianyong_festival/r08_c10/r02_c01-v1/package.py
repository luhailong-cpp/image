from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
ap=argparse.ArgumentParser();ap.add_argument('--joined',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
J=Path(a.joined);O=Path(a.out);O.mkdir(exist_ok=True)
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
cpfile=T/'source-checkpoint.json';cpstart=sha(cpfile);cp=read(cpfile)
fr=cp['fragment'];lr=cp['coupledNeighbors']['r08_c09']
for r in [fr,lr]:assert sha(r['file'])==r['sha256']
ctx=np.asarray(Image.open(P/'context-current.png').convert('RGBA'))
current=Image.new('RGBA',(1254,1254));current.paste(Image.open(lr['file']).convert('RGBA').crop((3981,909,4096,2163)),(0,0));current.paste(Image.open(fr['file']).convert('RGBA').crop((0,909,1139,2163)),(115,0))
cur=np.asarray(current);known=ctx[:,:,3]==255
assert np.array_equal(ctx[known],cur[known]),'Prospective context not pixel-identical to latest root; wait for middle commit or rebase consciously'
expected=np.ones((1254,1254),bool);expected[230:1024,115:1024]=False
assert np.array_equal(known,expected)
assert np.array_equal(cur[:,:,3]==255,expected),'Missing region ownership changed'
joined=Image.open(J).convert('RGB');arr=np.asarray(joined);assert arr.shape==(1254,1254,3)
changed=np.any(arr!=ctx[:,:,:3],axis=2)&known
specs=[('new-placement.png','r08_c10',[115,230,1024,1024],None)]
for n,tile,b,prior in [('left-return.png','r08_c09',[0,0,115,1254],lr),('top-return.png','r08_c10',[115,0,1254,230],fr),('right-return.png','r08_c10',[1024,230,1254,1024],fr),('bottom-return.png','r08_c10',[115,1024,1254,1254],fr)]:
 x0,y0,x1,y1=b;ys,xs=np.where(changed[y0:y1,x0:x1])
 if len(xs):specs.append((n,tile,[x0+int(xs.min()),y0+int(ys.min()),x0+int(xs.max())+1,y0+int(ys.max())+1],prior))
mask=np.zeros(known.shape,bool);patches=[]
for n,tile,b,prior in specs:
 joined.crop(b).save(O/n);mask[b[1]:b[3],b[0]:b[2]]=True
 dst=[b[0]+(3981 if tile=='r08_c09' else -115),b[1]+909,b[2]+(3981 if tile=='r08_c09' else -115),b[3]+909]
 patches.append({'asset':info(O/n),'cropFromJoinedLTRB':b,'destinationTile':tile,'destinationTileLTRB':dst,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True})
 save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(J)],'operation':'Exact native1:1 crop, no rescale','cropLTRB':b,'nativeScale':1,'newModelCalls':0})
assert np.array_equal(arr[known&~mask],ctx[:,:,:3][known&~mask])
save('source-validation.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'checkpoint':info(cpfile),'sourceVersion':cp['version'],'frozenContext':info(P/'context-current.png'),'sourceFiles':[fr,lr],'prospectiveContextNowPixelIdentical':True,'knownPixelsOutsideReturnsUnchanged':True,'missingNativePixels':int((~known).sum()),'formalAccepted':False})
save('patches-draft.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'joined':info(J),'windowTileLocalLTRB':[-115,909,1139,2163],'windowGlobalLTRB':[36749,29581,38003,30835],'patches':patches,'sourceValidation':info(O/'source-validation.json'),'newMissingPixelsFilled':int((~known).sum()),'nativeScale':1,'formalAccepted':False})
canvas=Image.new('RGBA',(1454,1454));canvas.paste(Image.open(lr['file']).convert('RGBA'),(-3881,-809));canvas.paste(Image.open(fr['file']).convert('RGBA'),(215,-809));canvas.paste(joined,(100,100));canvas.save(O/'surrounding-native.png')
save('surrounding-native.png.generation.json',{**info(O/'surrounding-native.png'),'derivedFrom':[info(J),fr,lr],'operation':'Native1:1 local context montage for review; no resizing','newModelCalls':0})
for n,b in [('outer-top.png',[0,0,1454,460]),('outer-bottom.png',[0,1020,1454,1454]),('outer-left.png',[0,0,460,1454]),('outer-right.png',[1020,0,1454,1454])]:
 canvas.crop(b).save(O/n);save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(O/'surrounding-native.png')],'operation':'Native1:1 QA crop','cropLTRB':b,'newModelCalls':0})
assert sha(cpfile)==cpstart,'Root checkpoint changed during packaging; retry from current snapshot'
print(json.dumps({'draft':info(O/'patches-draft.json'),'newPixels':int((~known).sum()),'sourceVersion':cp['version'],'patchCount':len(patches)}))

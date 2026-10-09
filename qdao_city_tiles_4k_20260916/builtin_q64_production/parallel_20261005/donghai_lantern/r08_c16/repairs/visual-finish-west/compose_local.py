from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;T=B.parent.parent;O=B/'output-refined';Q=B/'qa-refined'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def saved(p,a,rec):
    p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(p)
    write(Path(str(p)+'.generation.json'),{**ref(p),**rec});return ref(p)
pre=read(B/'prompts/s1.prepared.json')
base=pre['base'];west=pre['immutableWest']
assert sha(base['file'])==base['sha256'] and sha(west['file'])==west['sha256']
a=np.array(Image.open(base['file']).convert('RGB'));w=np.array(Image.open(west['file']).convert('RGB'))
ys=[0,1024,2048,2842];sources=[];ns=[]
for i in range(1,5):
    p=B/'native'/f's{i}.png';r=read(str(p)+'.generation.json');assert sha(p)==r['sha256']
    assert r['actualModel'] is None and r['actualQuality'] is None
    for e in r['references']:assert sha(e['file'])==e['sha256']
    cp=B/'calibrated-refined'/f's{i}.png';cr=read(str(cp)+'.generation.json');assert sha(cp)==cr['sha256'] and cr['maxAbsRGBField']<=24.00001
    assert cr['derivedFrom'][0]['sha256']==sha(p)
    ns.append(np.array(Image.open(cp).convert('RGB')));sources.append({**ref(cp),'record':ref(str(cp)+'.generation.json'),'rawNative':ref(p),'rawNativeRecord':ref(str(p)+'.generation.json'),'boundedRGBField':cr['field'],'maxAbsRGBField':cr['maxAbsRGBField']})
# Partition four source strips across only their real overlaps. Never resample/warp pixels.
weights=np.zeros((4,4096),np.float32)
for i,y in enumerate(ys):weights[i,y:y+1254]=1
for i in range(3):
    lo=ys[i+1];hi=ys[i]+1254;t=np.linspace(0,1,hi-lo,dtype=np.float32)
    fade=(1-np.cos(np.pi*t))/2
    weights[i,lo:hi]=1-fade;weights[i+1,lo:hi]=fade
assert np.max(np.abs(weights.sum(0)-1))<1e-5
patch=a.astype(np.float32).copy()
for i,y in enumerate(ys):
    if i==0:patch[:,:350]=0
    patch[y:y+1254,:350] += ns[i][:,627:977].astype(np.float32)*weights[i,y:y+1254,None,None]
# Fresh geometric masks: no inherited serrated/material-threshold masks.
xs=np.arange(4096)
fade=np.ones(4096,np.float32);fade[156:220]=(1+np.cos(np.pi*np.linspace(0,1,64)))/2;fade[220:]=0
alpha=np.broadcast_to(fade[None,:],(4096,4096)).copy()
def smooth_box(rect,feather):
    x0,y0,x1,y1=rect
    yy,xx=np.mgrid[y0:y1,x0:x1]
    distance=np.minimum.reduce([xx-x0,x1-1-xx,yy-y0,y1-1-yy]).astype(np.float32)
    z=np.clip(distance/feather,0,1);return (1-np.cos(np.pi*z))/2
island=np.zeros((4096,4096),np.float32);island[2070:2349,0:349]=smooth_box([0,2070,349,2349],36)
# Use dedicated s3 only for wood island; y2050..2350 is authorized, source y2048.
ii=island>0;isource=a.astype(np.float32).copy();isource[2048:3302,:350]=ns[2][:,627:977]
result=np.rint(a*(1-alpha[:,:,None])+patch*alpha[:,:,None]).clip(0,255).astype(np.uint8)
result=np.rint(result*(1-island[:,:,None])+isource*island[:,:,None]).clip(0,255).astype(np.uint8)
union=(alpha>0)|(island>0);allowed=np.zeros((4096,4096),bool);allowed[:,:220]=True;allowed[2050:2350,:350]=True
assert not np.any(union & ~allowed)
assert np.array_equal(result[~allowed],a[~allowed])
changed=np.any(result!=a,axis=2)
O.mkdir(exist_ok=True);Q.mkdir(exist_ok=True)
record={'operation':'local native-pixel strip compositing with fresh smooth masks and true-overlap crossfade; no image blur, warp or resampling','derivedFrom':[base]+sources,'unchangedWest':west,'priorRejectedFieldTrialUsed':False,'actualModel':None,'actualQuality':None,'modelEvidence':'See native per-image builtin records; no image generation occurs during composition.'}
candidate=saved(O/'r08_c16.png',result,record)
support=saved(O/'copy-support.png',(union*255).astype(np.uint8),{'operation':'binary COPY support for already-composited candidate; not a second blend alpha','derivedFrom':[candidate]})
np.savez_compressed(O/'fresh-alpha-and-joins.npz',seamAlpha=alpha.astype(np.float32),woodIslandAlpha=island.astype(np.float32),joinWeights=weights)
mask=saved(O/'blend-alpha.png',np.rint((1-(1-alpha)*(1-island))*255).astype(np.uint8),{'operation':'display of actual fresh combined blend alpha; use copy-support when integrating candidate','derivedFrom':[base]+sources})
pair=Image.fromarray(np.concatenate([w,result],axis=1))
qa=[]
windows=[]
for i,y in enumerate(ys,1):
    windows.extend([(f's{i}-actual-pair-full1254',[-627,y,627,y+1254]),(f's{i}-right-return',[100,y,450,y+1254])])
for i in range(3):windows.append((f'join-{i+1}-{i+2}',[-224,ys[i+1]-64,400,ys[i]+1254+64]))
windows += [('wood-island-return',[-100,2020,420,2390]),('top-return',[-224,0,350,224]),('bottom-return',[-224,3872,350,4096])]
for name,rect in windows:
    x0,y0,x1,y1=rect;crop=np.array(pair.crop((4096+x0,y0,4096+x1,y1)))
    entry=saved(Q/(name+'.png'),crop,{'operation':'exact actual immutable c15 plus new c16 pair crop','tileRectXYXY':rect,'derivedFrom':[west,candidate],'pixelScale':1,'resized':False,'visualReview':'pending'})
    entry['tileRectXYXY']=rect;qa.append(entry)
delta=np.abs(result.astype(np.int16)-a.astype(np.int16))
manifest={'generatedUtc':datetime.now(timezone.utc).isoformat(),'base':base,'immutableWest':west,'candidate':candidate,'copySupport':support,'freshBlendAlpha':mask,'freshAlphaAndJoinFields':ref(O/'fresh-alpha-and-joins.npz'),'nativeSources':sources,'nativeModelQuality':{'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None},'rejectedFieldUsed':False,'composition':'copy candidate where copy-support>0 only; candidate is already alpha blended. Do not alpha blend a second time.','authorizedScope':[[0,0,220,4096],[0,2050,350,2350]],'proof':{'outsideAuthorizedScopeChangedPixels':int(changed[~allowed].sum()),'outsideCopySupportChangedPixels':int(changed[~union].sum()),'changedPixels':int(changed.sum()),'immutableC15FileStillSameSha':sha(west['file'])==west['sha256'],'additionalRGBFieldApplied':True,'additionalRGBFieldMaxAbs':24,'RGBFieldEvidence':'same-coordinate actual c15 versus native left; robust smooth material-affine color map; no image blur','AIReplacementMaxRGBDelta':int(delta.max()),'x220PlusOutsideWoodExact':True,'allGeneratedNativeSizes':[list(n.shape[1::-1]) for n in ns]},'qa':qa,'formalAccepted':False,'visualReview':'pending'}
write(O/'manifest.json',manifest)
print(json.dumps({'candidate':candidate,'manifest':ref(O/'manifest.json'),'proof':manifest['proof'],'qaCount':len(qa)}))


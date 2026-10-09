from pathlib import Path
import json,hashlib,datetime,sys
from types import SimpleNamespace
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent.parent;R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def sm(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def bbox(mask):
 y,x=np.where(mask);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)] if len(y) else None
def save_derivative(p,a,source,stats,op):
 Image.fromarray(a).save(p);write(Path(str(p)+'.generation.json'),dict(**ref(p),createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),derivedFrom=source,operation=op,registration=stats,actualModel=None,actualQuality=None,sourceUpscaling=False,approvedForPromotion=False))
def qa(out,name,im,box,source):
 p=out/(name+'.png');im.crop(box).save(p);write(Path(str(p)+'.generation.json'),dict(**ref(p),derivedFrom=[ref(source)],operation=dict(cropLTRB=list(box),scale=1),actuallyViewed=False))
mode=sys.argv[1];D=T/'repairs'/('p24-water-join' if mode=='p24' else 'p11-north-leaves');out=D/'bounded-v1';out.mkdir(exist_ok=False);yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
if mode=='p24':
 host=D/'host-result.png';req=read(D/'repair.request.json');src=T/'native/p24.png';assert sha(src)==req['source']['sha256'];assert sha(T/'plan.json')==req['plan']['sha256'];g=Path(str(host)+'.generation.json');assert not g.exists()
 for x in req['references']:assert sha(x['file'])==x['sha256']
 sourcehost=Path('C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-9495e584-fba9-4ff9-90be-26a60052adf5.png');assert sha(host)==sha(sourcehost)
 write(g,dict(**ref(host),generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed; selectors and actual version/quality unavailable.',prompt=req['prompt'],references=req['references'],evidence=dict(sourceOutputPath=str(sourcehost),sourceOutputSha256=sha(sourcehost),resultId=sourcehost.stem),sourceUpscaled=False,resizedAfterGeneration=False,accepted=False))
 ctx=np.asarray(Image.open(T/'native/p24-context.png').convert('RGBA'));context=ctx[:,:,:3].copy();known=ctx[:,:,3]>0;layout=engine.Layout();edges=['right','top'];owner=engine.owner_mask(known,edges,layout)
 registered,flow,tone,stats=engine.register_native(context,ar(host),known,owner,edges,layout,max_shift=6.,tone_cap=18.,return_depth=256)
 original=ar(src);alpha=sm((yy-115)/60)*sm((520-yy)/70)*sm((1139-xx)/50);alpha[(yy<115)|(xx>=1139)]=0
 mixed=np.clip(np.rint(original*(1-alpha[:,:,None])+registered*alpha[:,:,None]),0,255).astype(np.uint8)
 # Native owner-free support is exact, not the altered generated pixels.
 mixed[~owner]=context[~owner]
 proposal=out/'p24-proposal.png';save_derivative(proposal,mixed,[ref(src),ref(host),ref(g),ref(T/'native/p24-context.png')],stats,dict(kind='bounded local AI water join replacement with exact real N/E ownership',compositeReturnLTRB=[0,115,1139,520],nativePixelScale=1))
 frame=Image.fromarray(mixed);checks=[('qa-water-join',(0,0,1254,400)),('qa-local-return',(0,380,1254,590)),('qa-east-boundary',(979,0,1254,1254)),('qa-left-rock',(0,65,270,560))]
else:
 host=D/'north-leaves-v1.png';req=read(D/'north-leaves-v1.request.json');src=T/'native/p11.png'
 for x in req['references']+req['sources']:assert sha(x['file'])==x['sha256']
 context=ar(D/'north-leaves-v1-target.png');known=yy<627;owner=~known;layout=SimpleNamespace(patch=1254,halo=627)
 registered,flow,tone,stats=engine.base.register_native(context,ar(host),known,owner,['top'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
 alpha=sm((850-xx)/100)*sm((947-yy)/128);alpha[known]=0
 mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+registered*alpha[:,:,None]),0,255).astype(np.uint8);assert np.array_equal(mixed[known],context[known])
 orig=Image.open(src).convert('RGB');orig.paste(Image.fromarray(mixed).crop((0,627,850,947)),(115,115));original=ar(src);proposal=out/'p11-proposal.png';save_derivative(proposal,np.asarray(orig),[ref(src),ref(host),ref(Path(str(host)+'.generation.json')),ref(D/'north-leaves-v1-target.png')],stats,dict(kind='native boundary-centered AI continuation with finite return',sourceCanvasGlobalXYWH=req['canvasGlobalXYWH'],cropLTRB=[0,627,850,947],pasteXY=[115,115],allowedP11LTRB=[115,115,965,435],numericBoundaryY=627,productionHalo115Unchanged=True))
 frame=Image.fromarray(mixed);framepath=out/'joint-frame.png';save_derivative(framepath,mixed,[ref(D/'north-leaves-v1-target.png'),ref(proposal)],stats,dict(kind='exact same-frame joint QA',trueNorthUnchanged=True));checks=[('qa-north-join',(0,467,1024,787)),('qa-return-y320',(0,837,1024,1087)),('qa-return-x850',(710,487,990,1087)),('qa-left-platform',(0,447,320,987))]
yyf,xxf=np.gradient(flow[:,:,0]);yyg,xxg=np.gradient(flow[:,:,1]);jac=(1+xxf)*(1+yyg)-yyf*xxg;used=alpha>0
np.save(out/'flow.npy',flow);np.save(out/'tone.npy',tone);np.save(out/'alpha.npy',alpha)
diag=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),script=ref(__file__),source=ref(src),host=ref(host),proposal=ref(proposal),registration=stats,actualMaxFlowInSelectedPixels=float(np.linalg.norm(flow[used],axis=1).max()),actualMaxToneInSelectedPixels=float(np.abs(tone[used]).max()),jacobianMinimumInSelectedPixels=float(jac[used].min()),nativeScale=1,changedBBoxLTRB=bbox(np.any(ar(proposal)!=original,axis=2)),approvedForPromotion=False,canonicalUnchanged=True)
assert diag['actualMaxFlowInSelectedPixels']<=6.00001 and diag['actualMaxToneInSelectedPixels']<=18 and diag['jacobianMinimumInSelectedPixels']>=.25
write(out/'diagnostic.json',diag)
for name,box in checks:qa(out,name,frame,box,proposal if mode=='p24' else framepath)
print(json.dumps(diag,indent=2))

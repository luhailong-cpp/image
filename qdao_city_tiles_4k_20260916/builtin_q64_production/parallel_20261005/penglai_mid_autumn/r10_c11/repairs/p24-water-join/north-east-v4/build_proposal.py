from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
req=read(D/'repair.request.json');assert sha(T/'plan.json')==req['plan']['sha256']
for source in req['sources']+req['references']:assert sha(source['file'])==source['sha256']
base=Path(req['sources'][0]['file']);north=Path(req['sources'][1]['file']);east=Path(req['sources'][2]['file']);host=D/'host-result.png'
b=ar(base);h=ar(host);n=ar(north);e=ar(east);p=b.copy();yy=np.arange(742)[:,None]+512
w=np.clip((1254-yy)/154,0,1);w=w*w*(3-2*w);w=np.broadcast_to(w,(742,1254)).copy();w[:230]=0;w[:,1139:]=0
p[:742]=np.clip(np.rint(b[:742]*(1-w[:,:,None])+h[512:1254]*w[:,:,None]),0,255).astype('uint8')
p[:230]=n[1024:1254];p[:,1139:]=e[909:2163,:115]
out=D/'p24-proposal.png';assert not out.exists();Image.fromarray(p).save(out)
context=np.zeros_like(p);known=np.zeros((1254,1254),bool);context[:230]=n[1024:1254];known[:230]=True;context[:,1139:]=e[909:2163,:115];known[:,1139:]=True
layout=engine.base.Layout();owner=engine.owner_mask(known,['top','right'],layout)
preview,flow,tone,stats=engine.register_native(context,p,known,owner,['top','right'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
previewpath=D/'p24-production-replay.png';Image.fromarray(preview).save(previewpath)
assert np.array_equal(p[known],context[known])
equal=np.array_equal(preview,p)
operation=dict(nativeScale=1,hostCropLTRB=[0,512,1254,1254],pasteXY=[0,0],selection=dict(fullUntilHostY=1100,zeroAtHostY=1254,knownNorthRows230Restored=True,knownEastColumns115Restored=True),geometryResampledInComposition=False,toneCorrectionInComposition=False,productionReplay=dict(engine=ref(R/'tools/multi_edge/engine.py'),options=dict(max_shift=6,tone_cap=18,return_depth=256),statistics=stats,byteIdenticalPixels=equal,maxRGBDelta=int(np.abs(preview.astype(int)-p.astype(int)).max()),knownSupportExact=True),canonicalUnchanged=True,approvedForPromotion=False)
write(D/'diagnostic.json',dict(proposal=ref(out),preview=ref(previewpath),sources=[ref(base),ref(host),ref(north),ref(east)],operation=operation))
for f in [out,previewpath]:write(str(f)+'.generation.json',dict(**ref(f),derivedFrom=[ref(base),ref(host),ref(north),ref(east)],hostGeneration=ref(str(host)+'.generation.json'),operation=ref(D/'diagnostic.json'),actualModel=None,actualQuality=None,approvedForPromotion=False))
# QA joint contains additional true N at y-512 and true E to +160.
joint=Image.new('RGB',(1299,1766));joint.paste(Image.open(north).convert('RGB').crop((0,512,1254,1254)),(0,0));joint.paste(Image.fromarray(preview),(0,512));joint.paste(Image.open(east).convert('RGB').crop((0,397,160,2163)),(1139,0));jp=D/'qa-joint-context.png';joint.save(jp)
write(str(jp)+'.generation.json',dict(**ref(jp),derivedFrom=[ref(previewpath),ref(north),ref(east)],operation=dict(globalFrameXYWH=[43917,37261,1299,1766],pastes=[dict(source=str(north),cropLTRB=[0,512,1254,1254],pasteXY=[0,0]),dict(source=str(previewpath),cropLTRB=[0,0,1254,1254],pasteXY=[0,512]),dict(source=str(east),cropLTRB=[0,397,160,2163],pasteXY=[1139,0])]),nativeScale=1,actuallyViewed=False))
boxes=[('qa-north-owner',[0,467,1254,787]),('qa-north-support-return',[0,582,1254,902]),('qa-east',[979,512,1299,1766]),('qa-northeast-corner',[979,467,1299,907]),('qa-south-local-return',[0,1094,1254,1414]),('qa-left-stone',[0,690,320,1240]),('qa-east-local-return',[720,800,1040,1766])]
for name,box in boxes:
 q=D/(name+'.png');joint.crop(box).save(q);write(str(q)+'.generation.json',dict(**ref(q),source=ref(jp),cropLTRB=box,nativeScale=1,actuallyViewed=False))
print(json.dumps(dict(proposal=ref(out),productionReplayPixelIdentical=equal,replayMaxDelta=operation['productionReplay']['maxRGBDelta'],knownSupportExact=True),indent=2))

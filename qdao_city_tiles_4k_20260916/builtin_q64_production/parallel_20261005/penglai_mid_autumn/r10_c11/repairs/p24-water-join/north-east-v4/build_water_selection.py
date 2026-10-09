from pathlib import Path
from PIL import Image
from types import SimpleNamespace
import numpy as np,json,hashlib,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
cv=engine.base.cv_module();O=D/'water-selection';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
req=read(D/'repair.request.json');base=Path(req['sources'][0]['file']);north=Path(req['sources'][1]['file']);east=Path(req['sources'][2]['file']);host=D/'host-result.png';context=D/'context.png'
for source in req['sources']+req['references']:assert sha(source['file'])==source['sha256']
b=ar(base);h=ar(host);a=ar(context);n=ar(north);e=ar(east);yy,xx=np.mgrid[:1254,:1254].astype(np.float32);known=yy<742
reg,flow,tone,stats=engine.base.register_native(a,h,known,~known,['top'],SimpleNamespace(patch=1254,halo=742),max_shift=6.,tone_cap=18.,return_depth=256)
# Select only already AI-painted water/stone. Protect all old and new leaf pixels plus a 24px margin.
def greens(z):return (z[:,:,1].astype(float)>z[:,:,2]*1.05)&(z[:,:,1].astype(float)>z[:,:,0]*1.05)
protect=cv.dilate((greens(a)|greens(reg)).astype('uint8'),np.ones((49,49),'uint8'))
distance=cv.distanceTransform(1-protect,cv.DIST_L2,5)
w=np.clip(distance/24,0,1)*np.clip((1254-yy)/154,0,1);w[yy<742]=0;w[xx>=1139]=0
w=w*w*(3-2*w)
mixed=np.clip(np.rint(a*(1-w[:,:,None])+reg*w[:,:,None]),0,255).astype('uint8')
p=b.copy();p[:742]=mixed[512:1254];p[:230]=n[1024:1254];p[:,1139:]=e[909:2163,:115]
out=O/'p24-proposal.png';Image.fromarray(p).save(out)
np.save(O/'flow.npy',flow);np.save(O/'tone.npy',tone);np.save(O/'selection.npy',w)
pc=np.zeros_like(p);pk=np.zeros((1254,1254),bool);pc[:230]=n[1024:1254];pk[:230]=True;pc[:,1139:]=e[909:2163,:115];pk[:,1139:]=True
layout=engine.base.Layout();owner=engine.owner_mask(pk,['top','right'],layout);preview,_,_,stats2=engine.register_native(pc,p,pk,owner,['top','right'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
previewpath=O/'p24-production-replay.png';Image.fromarray(preview).save(previewpath);assert np.array_equal(p[pk],pc[pk]) and np.array_equal(p,preview)
write(O/'diagnostic.json',dict(proposal=ref(out),sources=[ref(base),ref(host),ref(north),ref(east)],nativeScale=1,northRegistration=stats,selection=dict(kind='protect union of existing and newly generated green leaves by color-selection only; no pixel painting',greenRatio=1.05,protectedMarginPixels=24,selectionReturnPixels=24,lowerReturnStartHostY=1100,lowerReturnEndHostY=1254),productionReplay=dict(statistics=stats2,pixelIdentical=True,knownSupportExact=True),canonicalUnchanged=True,approvedForPromotion=False))
for f in [out,previewpath]:write(str(f)+'.generation.json',dict(**ref(f),derivedFrom=[ref(base),ref(host),ref(north),ref(east)],hostGeneration=ref(str(host)+'.generation.json'),operation=ref(O/'diagnostic.json'),actualModel=None,actualQuality=None,approvedForPromotion=False))
joint=Image.new('RGB',(1299,1766));joint.paste(Image.open(north).convert('RGB').crop((0,512,1254,1254)),(0,0));joint.paste(Image.fromarray(preview),(0,512));joint.paste(Image.open(east).convert('RGB').crop((0,397,160,2163)),(1139,0));jp=O/'qa-joint-context.png';joint.save(jp)
write(str(jp)+'.generation.json',dict(**ref(jp),derivedFrom=[ref(previewpath),ref(north),ref(east)],operation=dict(globalFrameXYWH=[43917,37261,1299,1766],pastes=[dict(source=str(north),cropLTRB=[0,512,1254,1254],pasteXY=[0,0]),dict(source=str(previewpath),cropLTRB=[0,0,1254,1254],pasteXY=[0,512]),dict(source=str(east),cropLTRB=[0,397,160,2163],pasteXY=[1139,0])]),nativeScale=1,actuallyViewed=False))
boxes=[('qa-north-owner',[0,467,1254,787]),('qa-north-support-return',[0,582,1254,902]),('qa-east',[979,512,1299,1766]),('qa-northeast-corner',[979,467,1299,907]),('qa-south-local-return',[0,1094,1254,1414]),('qa-left-stone',[0,690,320,1240]),('qa-east-local-return',[720,800,1040,1766])]
for name,box in boxes:
 q=O/(name+'.png');joint.crop(box).save(q);write(str(q)+'.generation.json',dict(**ref(q),source=ref(jp),cropLTRB=box,nativeScale=1,actuallyViewed=False))
print(json.dumps(dict(proposal=ref(out),northMaxDisplacement=stats['actualMaxDisplacementVector'],northMaxTone=stats['actualMaxColorCorrectionRGB'],productionReplayPixelIdentical=True),indent=2))

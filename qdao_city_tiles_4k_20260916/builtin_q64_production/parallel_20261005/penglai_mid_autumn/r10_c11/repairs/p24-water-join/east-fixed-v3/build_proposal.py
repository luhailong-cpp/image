from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
D=Path(__file__).resolve().parent;T=D.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
req=read(D/'repair.request.json');assert sha(T/'plan.json')==req['plan']['sha256']
for source in req['sources']+req['references']:assert sha(source['file'])==source['sha256']
base=D.parent/'host-result.png';host=D/'host-result.png';context=D/'context.png'
a=ar(context);h=ar(host);b=ar(base);xx=np.arange(1254)[None,:]
w=np.clip((xx-270)/128,0,1);w=w*w*(3-2*w);w=np.broadcast_to(w,(1254,1254)).copy();w[:,627:]=0
joint=np.clip(np.rint(a*(1-w[:,:,None])+h*w[:,:,None]),0,255).astype('uint8');assert np.array_equal(joint[:,627:],a[:,627:])
proposal=b.copy();proposal[:,512:1139]=joint[:,:627];proposal[:,1139:]=a[:,627:742]
out=D/'p24-east-proposal.png';assert not out.exists();Image.fromarray(proposal).save(out)
j=D/'joint-frame.png';Image.fromarray(joint).save(j)
operation=dict(nativeScale=1,geometryResampled=False,flowApplied=False,toneCorrectionApplied=False,alphaSelection=dict(kind='smoothstep selection of already AI-painted pixels',zeroUntilJointX=270,fullAfterJointX=398,realEastAtAndAboveX627Fixed=True),p24Mapping=dict(jointCropLTRB=[0,0,627,1254],pasteXY=[512,0],realEastCropLTRB=[627,0,742,1254],realEastPasteXY=[1139,0]),northRepairStillPending=True)
for p in [out,j]:write(str(p)+'.generation.json',dict(**ref(p),derivedFrom=[ref(base),ref(host),ref(context)],hostGeneration=ref(str(host)+'.generation.json'),operation=operation,actualModel=None,actualQuality=None,approvedForPromotion=False,canonicalUnchanged=True))
for name,box in [('qa-east-join',[467,0,787,1254]),('qa-local-return',[190,0,510,1254]),('qa-upper-water',[350,0,900,370]),('qa-lower-leaves',[350,800,900,1254])]:
 p=D/(name+'.png');Image.fromarray(joint).crop(box).save(p);write(str(p)+'.generation.json',dict(**ref(p),source=ref(j),cropLTRB=box,nativeScale=1,actuallyViewed=False))
print(json.dumps(dict(proposal=ref(out),joint=ref(j),rawRightResidualMean=float(np.abs(h[:,627:].astype(float)-a[:,627:].astype(float)).mean()),canonicalUnchanged=True)))

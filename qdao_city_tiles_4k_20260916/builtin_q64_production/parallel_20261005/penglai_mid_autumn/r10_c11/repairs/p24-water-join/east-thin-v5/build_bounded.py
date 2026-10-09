from pathlib import Path
from PIL import Image
from types import SimpleNamespace
import numpy as np,json,hashlib,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
O=D/'bounded';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
base=Path(json.loads((D/'repair.request.json').read_text())['sources'][0]['file']);host=D/'host-result.png';context=D/'context.png'
a=ar(context);h=ar(host);b=ar(base);yy,xx=np.mgrid[:1254,:1254].astype(np.float32);known=xx>=627;owner=~known
reg,flow,tone,stats=engine.register_native(a,h,known,owner,['right'],SimpleNamespace(patch=1254,halo=627),max_shift=6.,tone_cap=18.,return_depth=256)
w=np.clip((xx-500)/45,0,1);w=w*w*(3-2*w);w[known]=0
joint=np.clip(np.rint(a*(1-w[:,:,None])+reg*w[:,:,None]),0,255).astype('uint8');assert np.array_equal(joint[:,627:],a[:,627:])
proposal=b.copy();proposal[:,512:1139]=joint[:,:627];proposal[:,1139:]=a[:,627:742];proposal[:230]=b[:230]
out=O/'p24-east-proposal.png';Image.fromarray(proposal).save(out);j=O/'joint-frame.png';Image.fromarray(joint).save(j)
np.save(O/'flow.npy',flow);np.save(O/'tone.npy',tone);np.save(O/'selection.npy',w)
operation=dict(nativeScale=1,registration=stats,selection=dict(zeroUntilJointX=500,fullAfterJointX=545,realEastAtAndAboveX627Fixed=True),p24Mapping=dict(jointCropLTRB=[0,0,627,1254],pasteXY=[512,0],realEastCropLTRB=[627,0,742,1254],realEastPasteXY=[1139,0]),northRepairStillPending=False,wholeProposalVisualReviewPending=True)
write(O/'diagnostic.json',dict(proposal=ref(out),sources=[ref(base),ref(host),ref(context)],operation=operation,canonicalUnchanged=True,approvedForPromotion=False))
for p in [out,j]:write(str(p)+'.generation.json',dict(**ref(p),derivedFrom=[ref(base),ref(host),ref(context)],hostGeneration=ref(str(host)+'.generation.json'),operation=ref(O/'diagnostic.json'),actualModel=None,actualQuality=None,approvedForPromotion=False,canonicalUnchanged=True))
for name,box in [('qa-east-join',[467,0,787,1254]),('qa-local-return',[190,0,510,1254]),('qa-upper-water',[350,0,900,370]),('qa-lower-leaves',[350,800,900,1254])]:
 p=O/(name+'.png');Image.fromarray(joint).crop(box).save(p);write(str(p)+'.generation.json',dict(**ref(p),source=ref(j),cropLTRB=box,nativeScale=1,actuallyViewed=False))
print(json.dumps(dict(proposal=ref(out),registration=stats,canonicalUnchanged=True)))

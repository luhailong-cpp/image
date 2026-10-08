from pathlib import Path
import json,hashlib,sys
from types import SimpleNamespace
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent
sys.path.insert(0,str(R/"tools/multi_edge"));import engine
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out=D/"stage1-bounded";out.mkdir(exist_ok=False);mapping=read(D/"mapping.json")
context=np.asarray(Image.open(D/"four-quadrant-context1254.png").convert("RGB"));host=D/"root-v1.png";assert sha(host)=="fd05b45b4fef9b01edaf8eb33a393a24a9439bb5da519cec2e9d83f4916d40c0";patch=np.asarray(Image.open(host).convert("RGB"));assert patch.shape==(1254,1254,3)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32);known=yy<627;owner=~known
layout=SimpleNamespace(patch=1254,halo=627)
registered,flow,tone,stats=engine.base.register_native(context,patch,known,owner,["top"],layout,max_shift=6.,tone_cap=18.,return_depth=256)
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
alpha=smooth(xx/96)*smooth((1253-xx)/96)*smooth((947-yy)/128);alpha[yy<627]=0
mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+registered*alpha[:,:,None]),0,255).astype(np.uint8)
assert np.array_equal(mixed[known],context[known]);np.save(out/"alpha.npy",alpha);np.save(out/"flow.npy",flow);np.save(out/"tone.npy",tone)
e=Path(mapping["currentEastSource"]["file"]);w=Path(mapping["draftWestSource"]["file"]);assert sha(e)==mapping["currentEastSource"]["sha256"];assert sha(w)==mapping["draftWestSource"]["sha256"]
east=Image.open(e).convert("RGB");west=Image.open(w).convert("RGB")
east.paste(Image.fromarray(mixed).crop((627,627,1254,947)),(0,0))
ep=out/"r10_c12-proposal.png";east.save(ep)
west.paste(Image.fromarray(mixed).crop((0,627,627,947)),(512,115))
west.paste(east.crop((0,0,115,1139)),(1139,115))
wp=out/"p14-proposal.png";west.save(wp)
four=Image.fromarray(mixed);four.save(out/"joint-proposal.png")
npE=np.asarray(east);oldE=np.asarray(Image.open(e));npW=np.asarray(west);oldW=np.asarray(Image.open(w))
diffE=np.any(npE!=oldE,axis=2);diffW=np.any(npW!=oldW,axis=2)
def bbox(mask):
 ys,xs=np.where(mask);return [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;used=alpha>0
diag=dict(createdAt=datetime.now(timezone.utc).isoformat(),sourceAI=ref(host),sourceGeneration=ref(str(host)+".generation.json"),sourceContext=ref(D/"four-quadrant-context1254.png"),mapping=ref(D/"mapping.json"),script=ref(__file__),method="Exact native four-quadrant repair registration from top627 true N/NE support. Coordinate origin changed only numerically; production patch layout unchanged. Bounded flow6/tone18 return256; opaque AI composite returned to original by lower y947 and side96. No code-generated contours or artwork blur.",registration=stats,numericRepairLayout=dict(patch=1254,physicalNorthBoundaryY=627,productionStride1024Halo115Unchanged=True),actualMaxFlowInAppliedPixels=float(np.linalg.norm(flow[used],axis=1).max()),actualMaxToneInAppliedPixels=float(np.abs(tone[used]).max()),jacobianMinimumInAppliedPixels=float(jac[used].min()),mechanicalReturnDepth=256,AICompositeReturnDepthFromJoin=320,topTrueSourcesUnchanged=True,changedEastBBox=bbox(diffE),changedWestIncludingNewEastSupportBBox=bbox(diffW),currentCanonicalSource=ref(e),baseWest=ref(w),eastProposal=ref(ep),westProposal=ref(wp),r10c13ConsumedRight320PixelExact=bool(np.array_equal(npE[:,3776:],oldE[:,3776:])),sourceNativeP14Unchanged=ref(R/"r10_c11/native/p14.png"),approvedForPromotion=False,needsStage2=True)
assert diag["jacobianMinimumInAppliedPixels"]>=.25 and diag["actualMaxFlowInAppliedPixels"]<=6.00001 and diag["actualMaxToneInAppliedPixels"]<=18
write(out/"diagnostic.json",diag)
for p in [ep,wp,out/"joint-proposal.png"]:write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(host),mapping["currentEastSource"],mapping["draftWestSource"]],operation=ref(out/"diagnostic.json"),actualModel=None,actualQuality=None,approvedForPromotion=False))
for name,im,box in [("qa-joint-north",four,(0,447,1254,847)),("qa-joint-vertical",four,(467,447,787,1047)),("qa-joint-return",four,(0,807,1254,1067)),("qa-left-return",four,(0,527,216,1027)),("qa-right-return-pending-stage2",four,(1038,527,1254,1027)),("qa-p14-north",west,(0,0,1254,460)),("qa-p14-east-preserved",west,(1030,570,1254,850))]:
 p=out/(name+".png");im.crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),source=ref(out/"joint-proposal.png") if im==four else ref(wp),operation=dict(cropLTRB=box),nativeScale=1,actuallyViewed=False))
print(json.dumps(diag))


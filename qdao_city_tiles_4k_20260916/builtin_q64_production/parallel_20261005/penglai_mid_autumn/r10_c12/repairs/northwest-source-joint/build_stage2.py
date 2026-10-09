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
v=D/"stage2-active";out=D/"stage2-bounded";out.mkdir(exist_ok=False);req=read(v/"actual.request.json");raw=v/"host-result.png";source=Path("C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-187d7c84-b56c-4dbb-bfa3-c6491b673eb2.png")
host=Image.open(raw).convert("RGB");assert host.size==(1254,1254)
write(str(raw)+".generation.json",dict(**ref(raw),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format="PNG",tool="image_gen.imagegen",route="builtin",configSnapshot=req["configSnapshot"],submittedParameters=req["submittedParameters"],actualSubmitted=req["actualSubmitted"],actualModel=None,actualQuality=None,unverifiedReason="Host-managed builtin does not expose actual model/quality",evidence={"sourceOutputPath":str(source),"sourceOutputSha256":sha(source),"resultId":source.stem},prompt=req["prompt"],promptSha256=req["promptSha256"],references=req["references"],mapping=req["mapping"],approvedForPromotion=False))
context=np.asarray(Image.open(v/"context.png").convert("RGB"));patch=np.asarray(host);yy,xx=np.mgrid[:1254,:1254].astype(np.float32);known=yy<627;owner=~known
registered,flow,tone,stats=engine.base.register_native(context,patch,known,owner,["top"],SimpleNamespace(patch=1254,halo=627),max_shift=6.,tone_cap=18.,return_depth=256)
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
alpha=smooth((xx-32)/96)*smooth((1032-xx)/96)*smooth((947-yy)/128);alpha[yy<627]=0
mixed=np.clip(np.rint(context*(1-alpha[:,:,None])+registered*alpha[:,:,None]),0,255).astype(np.uint8);assert np.array_equal(mixed[known],context[known])
np.save(out/"flow.npy",flow);np.save(out/"tone.npy",tone);np.save(out/"alpha.npy",alpha)
stage1=D/"stage1-bounded";east=Image.open(stage1/"r10_c12-proposal.png").convert("RGB");west=Image.open(stage1/"p14-proposal.png").convert("RGB")
east.paste(Image.fromarray(mixed).crop((0,627,1254,947)),(384,0))
ep=out/"r10_c12-proposal.png";east.save(ep);west.paste(east.crop((0,0,115,1139)),(1139,115));wp=out/"p14-proposal.png";west.save(wp)
Image.fromarray(mixed).save(out/"stage2-proposal.png")
oldE=np.asarray(Image.open(T/"output/r10_c12.png"));diff=np.any(np.asarray(east)!=oldE,axis=2);ys,xs=np.where(diff)
dyu,dxu=np.gradient(flow[:,:,0]);dyv,dxv=np.gradient(flow[:,:,1]);jac=(1+dxu)*(1+dyv)-dyu*dxv;used=alpha>0
diag=dict(createdAt=datetime.now(timezone.utc).isoformat(),sourceAI=ref(raw),sourceGeneration=ref(str(raw)+".generation.json"),sourceStage1=ref(stage1/"r10_c12-proposal.png"),sourceContext=ref(v/"context.png"),mapping=ref(v/"mapping.json"),script=ref(__file__),operation="Second native1254 AI repair from actual upper627 support, source E x384..1638. Standard bounded flow6/tone18 return256, selected x416..1416 and y0..320 AI composite with96px side/128px bottom finite returns. Exact old N and all other production PNG pixels unchanged.",registration=stats,actualMaxFlowInAppliedPixels=float(np.linalg.norm(flow[used],axis=1).max()),actualMaxToneInAppliedPixels=float(np.abs(tone[used]).max()),jacobianMinimumInAppliedPixels=float(jac[used].min()),mechanicalReturnDepth=256,AICompositeReturnDepthFromJoin=320,changedEastBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],eastProposal=ref(ep),westProposal=ref(wp),r10c13ConsumedRight320Exact=bool(np.array_equal(np.asarray(east)[:,3776:],oldE[:,3776:])),canonicalEUnchanged=ref(T/"output/r10_c12.png"),canonicalP14Unchanged=ref(R/"r10_c11/native/p14.png"),approvedForPromotion=False)
write(out/"diagnostic.json",diag)
for p in [ep,wp,out/"stage2-proposal.png"]:write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(raw),ref(stage1/"r10_c12-proposal.png"),ref(stage1/"p14-proposal.png")],operation=ref(out/"diagnostic.json"),actualModel=None,actualQuality=None,approvedForPromotion=False))
north=Image.open(read(T/"output/manifest.json")["northSource"]).convert("RGB")
for i in range(4):
 lo=i*1024;band=Image.new("RGB",(1024,320));band.paste(north.crop((lo,3936,lo+1024,4096)),(0,0));band.paste(east.crop((lo,0,lo+1024,160)),(0,160));p=out/("qa-north-%d.png"%(i+1));band.save(p);write(str(p)+".generation.json",dict(**ref(p),sources=[ref(ep),ref(read(T/"output/manifest.json")["northSource"])],operation=dict(xRange=[lo,lo+1024],joinY=160),nativeScale=1,actuallyViewed=False))
for n,box in [("return-y256",(0,176,1536,400)),("return-y320",(0,240,1536,480)),("return-x416",(336,0,576,430)),("return-x1416",(1296,0,1536,430))]:
 p=out/("qa-"+n+".png");east.crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),source=ref(ep),operation=dict(cropLTRB=box),nativeScale=1,actuallyViewed=False))
for n,box in [("p14-north",(0,0,1254,460)),("p14-east",(780,0,1254,1254)),("p14-rock",(0,0,420,600)),("p14-north-return",(0,250,1139,490)),("p14-east-return",(740,115,1020,1254)),("p14-ne-corner",(894,0,1254,360)),("p14-old-y742",(0,652,1254,842))]:
 p=out/("qa-"+n+".png");west.crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),source=ref(wp),operation=dict(cropLTRB=box),nativeScale=1,actuallyViewed=False))
print(json.dumps(diag))


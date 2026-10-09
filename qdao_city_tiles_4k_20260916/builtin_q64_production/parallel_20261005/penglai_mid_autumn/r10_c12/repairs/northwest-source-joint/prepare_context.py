from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def save(name,im,operation,sources):
 p=D/name;assert not p.exists();im.save(p);write(str(p)+".generation.json",dict(**ref(p),createdAt=datetime.now(timezone.utc).isoformat(),operation=operation,sources=sources,nativeScale=1,sourceUpscaling=False,actuallyViewed=False,approvedForPromotion=False));return p
plan=read(R/"r10_c11/plan.json")
E=Path(plan["eastCandidate"]);N=Path(plan["northCandidate"]);NE=Path(plan["northEastCandidate"])
W=R/"r10_c11/repairs/p14-north-join/geometry-combined-v1/proposal-p14.png"
expected={E:plan["eastCandidateSha256"],N:plan["northCandidateSha256"],NE:plan["northEastCandidateSha256"],W:"d04c306b13de9713939eed9bcc3174c0c0bef8a6b66720b7432dc4eee8d62289"}
for p,h in expected.items():assert sha(p)==h
images={k:Image.open(p).convert("RGB") for k,p in dict(N=N,NE=NE,E=E,W=W).items()}
ops=[dict(role="actual r09_c11 N",source=ref(N),cropLTRB=[3469,3469,4096,4096],pasteXY=[0,0]),dict(role="actual r09_c12 NE",source=ref(NE),cropLTRB=[0,3469,627,4096],pasteXY=[627,0]),dict(role="unapproved current r10_c11 p14 combined proposal",source=ref(W),cropLTRB=[512,115,1139,742],pasteXY=[0,627]),dict(role="actual current r10_c12 E",source=ref(E),cropLTRB=[0,0,627,627],pasteXY=[627,627])]
im=Image.new("RGB",(1254,1254))
for op in ops:im.paste(Image.open(op["source"]["file"]).crop(op["cropLTRB"]),op["pasteXY"])
context=save("four-quadrant-context1254.png",im,dict(kind="exact native four-image crop/paste only",globalXYWH=[44429,36237,1254,1254],cornerXY=[627,627],sourceRegions=ops),[ref(p) for p in expected])
mapping=dict(canvasGlobalXYWH=[44429,36237,1254,1254],nativePixels=[1254,1254],NandNEContextDepth=627,EContextWidth=627,currentP14ContextWidth=627,physicalCornerXY=[627,627],regions=ops,immutableNorthSources=[ref(N),ref(NE)],draftWestSource=ref(W),currentEastSource=ref(E),inverseMapping=dict(E="canvas[x>=627,y>=627] -> r10_c12[x-627,y-627]",W="canvas[x<627,y>=627] -> p14[x+512,y-512]"),sourcePlanFreeze=ref(R/"r10_c11/plan.json"),allImagesAndPlansUnchanged=True)
write(D/"mapping.json",mapping)
# Direct actual N/E evidence excluding every pending r10_c11 pixel.
for name,lo,hi,above,below in [("qa-source-northwest-native.png",0,1254,240,320),("qa-source-next-native.png",1024,2048,160,160),("qa-source-edge115-only.png",0,115,115,245)]:
 band=Image.new("RGB",(hi-lo,above+below));band.paste(images["NE"].crop((lo,4096-above,hi,4096)),(0,0));band.paste(images["E"].crop((lo,0,hi,below)),(0,above))
 save(name,band,dict(kind="actual r09_c12/r10_c12 source-only seam",topCropLTRB=[lo,4096-above,hi,4096],bottomCropLTRB=[lo,0,hi,below],joinY=above),[ref(NE),ref(E)])
a=np.asarray(images["NE"]).astype(np.float32);b=np.asarray(images["E"]).astype(np.float32)
delta=b[0]-a[-1];bins=[]
for lo in range(0,1536,128):
 z=delta[lo:lo+128];bins.append(dict(xRange=[lo,lo+128],medianSignedRGB=np.median(z,axis=0).tolist(),p95MaxAbsRGB=float(np.percentile(np.max(np.abs(z),axis=1),95)),maxAbsRGB=float(np.abs(z).max())))
samples=[dict(x=x,northLastRGB=a[-1,x].astype(int).tolist(),eastFirstRGB=b[0,x].astype(int).tolist(),jumpRGB=delta[x].astype(int).tolist()) for x in [0,16,32,64,100,160,256,384,512,640,768,896,1024,1152]]
write(D/"source-boundary-numerical.json",dict(sourceCurrent=ref(E),sourceNorth=ref(NE),method="Raw adjacent native source rows: E row0 minus NE row4095. No correction or interpolation. Numbers alone never constitute visual failure/pass.",xBins=bins,samples=samples,geometryOrToneRequiresVisualQA=True))
print(json.dumps(dict(context=ref(context),bins=bins,samples=samples)))


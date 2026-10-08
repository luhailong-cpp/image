from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
m=json.loads((D/"mapping.json").read_text());req=json.loads((D/"request.json").read_text())
C=Path(m["candidate"]["file"]);assert sha(C)==m["candidate"]["sha256"]
host=D/"host-result.png";hi=Image.open(host).convert("RGBA");assert hi.size==(1254,1254) and hi.getchannel("A").getextrema()==(255,255)
source="C:/Users/luyua/.codex/generated_images/01a11b0f-f960-71e1-a23f-11564ac63532/exec-5b866570-774f-46ab-80d0-9629412d903f.png"
meta=dict(file=str(host),sha256=sha(host),generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),nativeSize=[1254,1254],format="PNG",tool="image_gen.imagegen",route="builtin",hostSourceFile=source,hostSourceSHA256=sha(source),toolResultID="exec-5b866570-774f-46ab-80d0-9629412d903f",configSnapshot=req["configSnapshot"],submittedParameters=dict(model=None,quality=None,**req["actualSubmitted"]),actualModel=None,actualQuality=None,unverifiedReason=req["unverifiedReason"],prompt=req["prompt"],actualSubmittedPromptSHA256=req["actualSubmittedPromptSHA256"],references=req["references"],request=dict(file=str(D/"request.json"),sha256=sha(D/"request.json")),evidence=dict(toolResponse="Generated image saved by host to exact hostSourceFile; no model/quality metadata disclosed."),approved=False)
write(D/"host-result.png.generation.json",meta)
mask=Image.open(D/"replacement-mask.png").convert("L")
before=Image.open(D/"input-original.png").convert("RGBA");frame=before.copy();frame.paste(hi,(0,0),mask);frame.save(D/"proposal-frame.png")
candidate=Image.open(C).convert("RGBA");proposal=candidate.copy();proposal.paste(hi,m["localOrigin"],mask);proposal.save(D/"proposal-candidate.png")
a,b=np.array(candidate),np.array(proposal);diff=np.any(a!=b,axis=2);gm=Image.new("L",candidate.size,0);gm.paste(mask,m["localOrigin"]);assert not np.any(diff&(np.array(gm)==0))
ys,xs=np.where(diff)
change=dict(changedPixelCount=int(diff.sum()),changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],outsideMaskPixelChanges=0,candidateUnchanged=sha(C)==m["candidate"]["sha256"])
for name,box in [("qa-detail.png",[560,2510,1230,3130]),("qa-wall-post-joint.png",[740,2640,1020,2970]),("qa-repair-surround.png",[680,2570,1140,3080])]:
 f=D/name;proposal.crop(box).save(f)
 write(D/(name+".generation.json"),dict(file=str(f),sha256=sha(f),operation="Exact native crop",derivedFrom=[dict(file=str(D/"proposal-candidate.png"),sha256=sha(D/"proposal-candidate.png"))],sourceRect=box))
for name in ["proposal-frame.png","proposal-candidate.png"]:
 f=D/name;write(D/(name+".generation.json"),dict(file=str(f),sha256=sha(f),operation="Binary-mask exact native pixel replacement from AI host; no resizing, interpolation or painting.",derivedFrom=[m["candidate"],dict(file=str(host),sha256=sha(host),generationRecord=str(D/"host-result.png.generation.json"))],mapping=dict(file=str(D/"mapping.json"),sha256=sha(D/"mapping.json")),checks=change,approved=False,actualModel=None,actualQuality=None))
write(D/"proposal-checks.json",dict(**change,proposal=dict(file=str(D/"proposal-candidate.png"),sha256=sha(D/"proposal-candidate.png")),visualReviewPending=True,approved=False))
print(json.dumps(change))


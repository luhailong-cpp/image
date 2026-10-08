from pathlib import Path
import json,hashlib,argparse
from datetime import datetime,timezone
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
ap=argparse.ArgumentParser();ap.add_argument("--stage1-source");ap.add_argument("--stage1-sha");ap.add_argument("--name",default="stage2-preview");args=ap.parse_args()
if args.stage1_source and not args.stage1_sha:raise ValueError("Explicit source SHA required")
if not args.name.replace("-","").isalnum():raise ValueError("Name must be simple")
out=D/args.name;out.mkdir(exist_ok=False);m=read(T/"output/manifest.json");north=Path(m["northSource"]);source=Path(args.stage1_source) if args.stage1_source else Path(m["file"])
if args.stage1_source:assert sha(source)==args.stage1_sha
assert Image.open(source).size==(4096,4096)
# Covers r10_c12 x384..1638. Rebuild from approved stage1 full E candidate before submission.
lo=384;hi=1638;split=627;im=Image.new("RGB",(1254,1254));im.paste(Image.open(north).crop((lo,3469,hi,4096)),(0,0));im.paste(Image.open(source).crop((lo,0,hi,627)),(0,627));im.save(out/"context.png")
# Lower half only. Upper true N remains opaque. Left128 gives original/approved stage1 support; right286 protects wall/shore.
hole=[128,627,968,843];target=im.convert("RGBA");target.paste((0,0,0,0),hole);target.save(out/"edit-target.png")
mapping=dict(canvasGlobalXYWH=[45440,36237,1254,1254],scale=1,sourceNorth=ref(north),sourceCurrent=ref(source),sourceRegions=[dict(source=ref(north),cropLTRB=[lo,3469,hi,4096],pasteXY=[0,0]),dict(source=ref(source),cropLTRB=[lo,0,hi,627],pasteXY=[0,627])],trueNorthContextDepth=627,holeLTRB=hole,holeInR10C12LTRB=[512,0,1352,216],suggestedApplyMaximumR10C12LTRB=[480,0,1384,256],returnMustBeActuallyReviewed=True,oldNorthNeverChanged=True,scaleNeverChanged=True,rebuildFromApprovedStage1BeforeSubmission=not bool(args.stage1_source),submissionAllowed=bool(args.stage1_source),notes="This is preparation only. No AI call, output approval or production mutation. Stage1 overlaps r10_c12 x0..627. Stage2 extends across the observed source defect's right end; rebuild its opaque overlap from the accepted stage1 full-current-source proposal, never from an AI-only rectangular source crop.")
write(out/"mapping.json",mapping)
prompt="""Fill only the small transparent northern water strip in Image1, at its unchanged1254x1254 native scale. Continue the broad existing cobalt-blue water cells and cyan wave curves downward from the exact actual finished upper half, removing the erroneous straight horizontal color and contour cutoff at the opening's top. Join the unmodified water below and to the sides, keeping the broad cell positions and natural soft painted material. No rectangular tone patch, tiny subdivided waves, extra reflections, glints, foam or objects. Keep the upper half pixel placement, right stone wall/shore, and all outside geometry unchanged. Image2 is approved hand-painted style only. Return the same frame fully opaque."""
(out/"draft.prompt.txt").write_text(prompt,encoding="utf-8")
write(out/"draft.call.json",dict(prompt=prompt,referenced_image_paths=[str(out/"edit-target.png"),"D:/work/image/designs/gameplay-ui/04-guild.png"],transparent_background=False))
for name in ["context.png","edit-target.png"]:write(str(out/name)+".generation.json",dict(**ref(out/name),operation="Exact native source crop/paste plus alpha hole only, no AI generation.",mapping=ref(out/"mapping.json"),actuallyViewed=False,nativeScale=1))
print(str(out))


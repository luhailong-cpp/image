from pathlib import Path
import json,hashlib,datetime
from PIL import Image
R=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn/r10_c14")
D=R/"repairs/p31-beam-wall"
D.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
C=R/"output/r10_c14-candidate.png"
assert sha(C)=="0bbb59af2bb936e4d27945ea77240a56f0d34d4f887a24e4664c4ceb7d6a9e8c"
notes=[
("internal-y1024-full.png","Complete folded native seam viewed: large paving grout, highlights, capstone and post remain continuous, with broad clean brushwork."),
("internal-y2048-full.png","Complete folded native seam viewed: coping, wall block courses, pier and water connect without displaced endpoints or a straight color band."),
("internal-y3072-full.png","Complete folded native seam viewed: railing, planks, posts and water retain continuous outlines and material."),
("internal-y1024-return-256-full.png","Complete finite correction return line viewed: broad paving paint, coping, stone wall and post show no cutoff line."),
("internal-y2048-return-256-full.png","Complete finite correction return line viewed: wall courses, pier and water reflections show no rectangular return band."),
("internal-y3072-return-256-full.png","Complete finite correction return line viewed: post bases, wood grain, deck and water remain continuous."),
("junction-1024-1024.png","Native junction viewed: broad painted stone faces and grout corners join cleanly."),
("junction-2048-1024.png","Native junction viewed: rounded cap and post highlight have continuous shape."),
("junction-3072-1024.png","Native junction viewed: vertical wall grout and large stone faces are continuous."),
("junction-1024-2048.png","Native junction viewed: diagonal stone courses and highlight continue across the intersection without a step."),
("junction-2048-2048.png","Native junction viewed: large blue-purple stone paint and left grout are coherent with no cross-shaped stitch."),
("junction-3072-2048.png","Native junction viewed: warm pier edge, dark wall and blue water contours connect without doubled lines."),
("junction-1024-3072.png","Native junction viewed: diagonal railing highlights, plank joints and post remain aligned."),
("junction-2048-3072.png","Native junction viewed: wood plank grain and dark diagonal joint continue smoothly."),
("junction-3072-3072.png","Native junction viewed: round post, rope, railing and water retain clean continuous contours.")]
items=[]
for n,review in notes:
 f=R/"qa/native-candidate"/n
 items.append(dict(file=str(f),sha256=sha(f),actuallyViewed=True,nativeScale=1,verdict="scoped_pass",review=review,viewTool="view_image; detail=original"))
report=dict(reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer="/root/r09c14_row3_resume",candidate=dict(file=str(C),sha256=sha(C)),scope="Three complete horizontal internal seams, their three 256-pixel return lines, and nine four-way internal junctions. Does not certify unrelated body details or external seams.",items=items,scopedPass=True,issueCount=0,issues=[],formalAccepted=False,wholeTilePassed=False,knownOutsideScopeIssue=dict(file=str(R/"qa/p31-beam-wall-root-detail.png"),review="Actually viewed root detail crop and whole tile preview: transparent short beam behind large post overlays stone wall and grout. Local repair required; no whole tile acceptance."))
write(R/"qa/horizontal-review.json",report)
rect=[256,2250,1510,3504]
f=D/"input-original.png"
Image.open(C).convert("RGBA").crop(rect).save(f)
write(D/"input-original.png.generation.json",dict(file=str(f),sha256=sha(f),operation="Exact native-scale crop; no resize, rotation, reflection, paint or resampling.",derivedFrom=[dict(file=str(C),sha256=sha(C))],sourceRect=rect,outputSize=[1254,1254],actualModel=None,actualQuality=None,generatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat()))
write(D/"mapping.json",dict(candidate=dict(file=str(C),sha256=sha(C)),sourceRect=rect,localOrigin=rect[:2],proposalOnly=True,approved=False))
print(json.dumps(dict(horizontalReport=str(R/"qa/horizontal-review.json"),repairFrame=str(f),sha256=sha(f))))


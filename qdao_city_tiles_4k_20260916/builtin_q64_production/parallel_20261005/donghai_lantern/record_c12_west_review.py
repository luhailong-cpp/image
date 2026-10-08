"""Record the 22 native QA images actually visually reviewed by c12_west_final."""
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib

ROOT=Path(__file__).resolve().parent/'r08_c12/west-final'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p=Path(p).resolve()
    assert p.is_relative_to(ROOT.resolve())
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

manifest_path=ROOT/'output/west-final-manifest.json'
m=read(manifest_path)
expected=['common-edge-return-part%02d.png'%i for i in range(1,5)]
expected+=['attachment-%s-return-part%02d.png'%(side,i) for side in ('left','right') for i in range(1,5)]
expected+=['longitudinal-%d-return.png'%i for i in range(1,4)]
expected+=['corner-%s-%s.png'%(side,edge) for side in ('left','right') for edge in ('top','bottom')]
expected+=['attachment-top-full.png','attachment-bottom-full.png','old-c12-roof-line-focus.png']
assert {Path(q['file']).name for q in m['qa']}==set(expected)
for q in m['qa']:assert sha(q['file'])==q['sha256']
for out in m['outputs']:assert sha(out['file'])==out['sha256']
review={
 'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'Codex /root/c12_west_final',
 'method':'Actual view_image detail original on each of 22 saved native-pixel QA images; downscaled overview additionally inspected but excluded from native acceptance evidence.',
 'result':'pass-for-c11-c12-common-strip-and-attachment-scope',
 'formalAccepted':False,'clientAccepted':False,'wholeCityComplete':False,
 'outputBindings':m['outputs'],
 'actualImagesViewed':[{'file':q['file'],'sha256':q['sha256'],'pixels':q['pixels'],'pairRectXYXY':q['pairRectXYXY'],'pixelScale':1} for q in m['qa']],
 'coverage':{'commonEdge':{'lengthPixels':4096,'nativeReturnWidthPixels':512},'leftAndRightAttachments':{'eachLengthPixels':4096,'eachNativeReturnWidthPixels':896},'longitudinalReturnBands':3,'insertionCorners':4,'topAndBottomChangedBoundaries':True,'specificRoofLineFocus':True},
 'observations':[
   'Full c11/c12 common edge: diagonal roof beam, plaster/window, orange-red awning, timber posts and paving remain continuous; no seam stripe, duplicated contour or missing segment observed.',
   'Both full strip insertion returns: blue roof tile edges, red roof tile edges, timber/plaster boundaries, foliage and stone paving have continuous contour and light falloff. No additional actionable return seam found.',
   'All three longitudinal overlaps plus bounded RGB falloffs inspected at native scale. No hard horizontal cutoff, false broad shadow or geometry jump observed.',
   'Former c12 x<64 around y1139 roof lighting line is absent after common-strip insertion. Orange-red terracotta material is preserved.',
   'Four insertion corners and complete modified top/bottom boundary crops inspected; no artifact within supplied pair observed.'
 ],
 'unresolvedIssuesWithinReviewedScope':[],
 'limitations':[
   'North and south neighboring map tiles were not supplied; external cross-tile continuity and four-tile junctions remain pending.',
   'This scoped review does not accept the whole tiles, whole map, client closest-camera presentation, or final gameplay integration.',
   'Mechanical assembly uses the exact DAY masks without geometry flow or spatial resampling. AI edit geometry correspondence is visually constrained; pixel-identical cross-appearance geometry is not asserted.'
 ],
 'pixelProof':m['pixelVerification'],'formalAcceptanceInferredFromMetrics':False,
}
p=ROOT/'qa/review.json';write(p,review)
binding={'file':str(p),'sha256':sha(p),'result':review['result']}
m['status']='complete-pixel-candidates-common-strip-native-review-passed'
m['visualReview']=binding;m['qaCoverage']['visualReview']=binding
for q in m['qa']:q['visualReview']='pass-within-described-scope'
write(manifest_path,m)
for out in m['outputs']:
    p=Path(out['generationRecord']);r=read(p);r['visualReview']=binding;write(p,r)
print(json.dumps({'review':binding,'manifest':{'file':str(manifest_path),'sha256':sha(manifest_path)},'outputBindings':m['outputs']},indent=2))

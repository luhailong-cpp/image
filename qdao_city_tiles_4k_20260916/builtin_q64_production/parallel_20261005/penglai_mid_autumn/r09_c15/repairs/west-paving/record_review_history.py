from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
notes={
5:'Rejected: clipped color blend did not restore original pixels at opacity-zero boundaries; upper horizontal and lower true-west step remain.',
6:'Rejected: binary insertion of the two local AI crops created fresh small rectangular paint edges.',
7:'Rejected: local color matching and16px alpha return still leave upper horizontal and lower-west patch edges.',
8:'Parent inspected four perimeters: upper and right accepted locally; lower true-west groove/material endpoint still has a vertical cutoff.',
9:'Upper side-opacity return refined; lower region identical to v8 and unresolved. Do not apply as final.',
10:'Rejected: direct row color endpoint matching creates false horizontal stripes because dark groove and bright bevel endpoints still differ geometrically.',
11:'Parent reported actual original views of four perimeters and lower detail still show a direct cut. Rejected; current agent did not claim a fresh view in this resumed turn.',
13:'Rejected after original three-crossings crop: native v12 geometry and bevel widths remain inconsistent; bounded dynamic profile correspondence produces local bends. No application.',
14:'Rejected after original three-crossings and lower-detail crops: new AI v14 has continuous native strokes, but direct insertion into fixed oldW leaves 1..3px context drift and visible endpoint steps.',
15:'Rejected after original three-crossings and lower-detail crops: constant measured per-crossing shifts improve line centers but do not match all groove/bevel widths.',
16:'Rejected after original three-crossings and lower-detail crops: transporting high-gradient endpoint color along fixed rows creates false horizontal stripes.',
17:'Rejected after original three-crossings and lower-detail crops: transporting along observed diagonal directions improves bottom but color support128px creates extra tint marks near middle curve.',
18:'Pending parent review: bottom groove/bevel continuation improved with fresh AI v14, single-source cumulative flow<=5.2454px, positive Jacobian and color<=18. Upper/right perimeter remain clean. Small paint/contrast steps near upper and middle true-west crossings remain concerns; no complete seam pass claimed.'
}
for n,note in notes.items():
 q=P/f'review-v{n}.json'
 if q.exists():continue
 mapping=json.loads((P/f'proposal-v{n}.json').read_text())
 if n in range(5,11): names=[f'{s}-v{n}.png' for s in ['upper-perimeter','right-perimeter','lower-perimeter','west-join']];full=True
 elif n==11:names=[];full=False
 elif n==13:names=['three-crossings-v13.png'];full=False
 elif n==18:names=[f'{s}-v18.png' for s in ['upper-perimeter','right-perimeter','lower-perimeter','west-join','lower-detail','three-crossings']];full=True
 else:names=[f'three-crossings-v{n}.png',f'lower-detail-v{n}.png'];full=False
 items=[]
 for name in names:
  rec=next(r for r in mapping['qa'] if Path(r['file']).name==name)
  items.append({**rec,'actuallyViewed':True,'nativeScale':1,'verdict':'pending_root_review' if n==18 else 'rejected','review':note})
 write(q,{'recordedAt':now,'reviewer':'/root/r09c14_row2_resume','joint':ref(P/f'proposed-joint-v{n}.png'),'jointActuallyViewed':full,'nativeScale':1,'items':items,'reviewSummary':note,'accepted':False,'candidateUnchanged':True,'issues':[note],'rootReportedViews':n==11,'noAutomatedMetricTreatedAsVisualPass':True})
for name,source,box in [('lower-seam-diagnostic-v9.png','proposed-joint-v9.png',[256,830,480,1050]),('v12-seam-measurement.png','root-lower-bevel-v12.png',[550,0,720,920])]:
 p=P/name;g=Path(str(p)+'.generation.json')
 if p.exists() and not g.exists():write(g,{**ref(p),'recordedAt':now,'operation':'Exact unscaled native diagnostic crop','derivedFrom':ref(P/source),'cropLTRB':box,'sourcePixelScale':1,'actuallyViewed':True})
# Append clarification without changing historical proposal bytes or hash-linked records.
write(P/'proposal-v18-method-addendum.json',{'recordedAt':now,'proposal':ref(P/'proposal-v18.json'),'script':ref(P/'build_v18_endpoint_proposal.py'),'clarification':'Actual v18 endpoint color uses the bounded all-pixel endpoint residual, transported along observed native diagonal slopes, with horizontal support only32px. The same-material mask is a saved diagnostic from earlier alternatives and does not select the final v18 color field. Flow is relative to new native v14 source, zero inherited v4 flow; unmodified v9 background retains its own separately recorded provenance.','nativeSourceBoxesLTRB':[[627,65,807,150],[627,310,807,490],[627,790,807,895]],'additionalChangedCandidateBoundingLimitLTRB':[0,2907,180,3737],'originalProposalAuthorizedSupersetLTRB':[0,2842,300,3750],'candidateNotChanged':True})
missing=[]
for q in P.rglob('*'):
 if q.suffix.lower() in ['.png','.npy'] and not Path(str(q)+'.generation.json').exists():missing.append(str(q))
write(P/'local-sidecar-audit.json',{'recordedAt':now,'missingSidecars':missing,'allBinarySidecarsExist':not missing,'candidate':ref(P.parent.parent/'output/r09_c15-candidate.png'),'latestIndependentProposal':ref(P/'proposal-v18.json'),'latestReview':ref(P/'review-v18.json'),'candidateUnchanged957':sha(P.parent.parent/'output/r09_c15-candidate.png')=='957194bcbf888cac88f8b0a3d79d055f8ce69a76846590f174eee7e6f8b9e456'})
print(json.dumps({'missing':missing,'v18Review':ref(P/'review-v18.json')}))


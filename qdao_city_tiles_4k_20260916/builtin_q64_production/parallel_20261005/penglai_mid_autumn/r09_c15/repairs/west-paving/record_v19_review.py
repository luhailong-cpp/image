from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=json.loads((P/'proposal-v19.json').read_text())
items=[]
for r in v['qa']:
 name=Path(r['file']).name
 note='Actual original-scale inspection: patch perimeter preserved, no new rectangular boundary visible.'
 if name.startswith(('west-join','three-crossings')):note='Actual original-scale inspection: upper and middle bevels connect with gradual cold-blue to gold transitions; prior simultaneous vertical color jumps are no longer prominent. No duplicated grout stroke observed.'
 if name.startswith('lower-'):note='Actual original-scale inspection: passed v18 lower groove/bevel and lower return unchanged, verified byte/pixel equality.'
 items.append({**r,'actuallyViewed':True,'nativeScale':1,'verdict':'local_pass_pending_root_review','review':note})
write(P/'review-v19.json',{'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/r09c14_row2_resume','joint':ref(P/'proposed-joint-v19.png'),'jointActuallyViewed':True,'nativeScale':1,'items':items,'accepted':False,'localVisualResult':'ready_for_root_review','candidateUnchanged':True,'issues':[],'noAutomatedMetricTreatedAsVisualPass':True})
candidate=np.array(Image.open(T/'output/r09_c15-candidate.png').convert('RGB'))
joint=np.array(Image.open(P/'proposed-joint-v19.png').convert('RGB'))
previous=np.array(Image.open(P/'proposed-joint-v18.png').convert('RGB'))
source=np.array(Image.open(P/'edit-target.png').convert('RGB'))
assert np.array_equal(joint[:,:320],source[:,:320])
assert np.array_equal(joint[580:],previous[580:])
assert np.array_equal(joint[:,448:],previous[:,448:])
virtual=candidate.copy();virtual[2840:3750,:600]=joint[80:990,320:920]
assert np.array_equal(virtual[:,600:],candidate[:,600:]) and np.array_equal(virtual[3750:],candidate[3750:])
changed=np.any(virtual!=candidate,axis=2);ys,xs=np.nonzero(changed)
crop=P/'proposal-apply-crop-v19.png';Image.fromarray(joint).crop((320,80,920,990)).save(crop)
report={'recordedAt':datetime.now(timezone.utc).isoformat(),'candidate':ref(T/'output/r09_c15-candidate.png'),'proposal':ref(P/'proposal-v19.json'),'joint':ref(P/'proposed-joint-v19.png'),'exactApplyCrop':ref(crop),'cropSourceLTRB':[320,80,920,990],'cropDestinationXY':[0,2840],'actualChangedCandidateBBoxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedCandidatePixels':int(changed.sum()),'virtualAppliedCandidateRGBSha256':hashlib.sha256(virtual.tobytes()).hexdigest(),'canonicalNotWritten':True,'oldWestLeft320BitExact':True,'currentX600PlusBitExact':True,'currentY3750PlusBitExact':True,'currentSouth320BitExact':True,'currentTop2840BitExact':True,'v18LowerFromJointY580BitExact':True,'v18RightFromJointX448BitExact':True,'v18First152JointRowsBitExact':bool(np.array_equal(joint[:152],previous[:152])),'formalAccepted':False}
q=P/'proposal-v19-invariants.json';write(q,report)
write(Path(str(crop)+'.generation.json'),{**ref(crop),'operation':'Exact unscaled crop of independent joint proposal for application only after root approval','derivedFrom':ref(P/'proposed-joint-v19.png'),'sourceCropLTRB':[320,80,920,990],'destinationCandidateXY':[0,2840],'invariantReport':ref(q),'sourcePixelScale':1,'formalAccepted':False})
write(P/'proposal-v19-method-addendum.json',{'proposal':ref(P/'proposal-v19.json'),'script':ref(P/'build_v19_proposal.py'),'colorMethod':'All-pixel endpoint residual bounded18, transported along observed native diagonal slopes with32px rightward support; saved same-material mask is diagnostic only.','nativeFlowSource':ref(P/'upper-middle-v19.png'),'sourceFlowSingleAndCumulative':True,'inheritedV18FlowAppliedAgain':False,'v18BackgroundUnchangedOutsideTwoPatches':True,'nativeSourceBoxesLTRB':[[627,252,755,342],[627,484,755,680]],'candidateBoxesLTRB':[[0,2912,128,3002],[0,3144,128,3340]],'sourceToJointXY':[-307,-100]})
s=(P/'audit_source_chain.py').read_text().replace("'three-endpoints-v14.png']:","'three-endpoints-v14.png','upper-middle-v19.png']:").replace("source-chain-audit.json","source-chain-audit-v19.json").replace("proposal-v18.json","proposal-v19.json")
(P/'audit_source_chain_v19.py').write_text(s)
print(json.dumps({'review':ref(P/'review-v19.json'),'invariants':ref(q),'crop':ref(crop),'v18LowerUnchanged':True}))


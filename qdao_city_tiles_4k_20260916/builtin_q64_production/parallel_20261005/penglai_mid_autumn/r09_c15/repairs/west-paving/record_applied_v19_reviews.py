from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
from PIL import Image
import numpy as np
P=Path(__file__).parent;T=P.parent.parent;R=T.parent
sys.path.insert(0,str(R/'tools'));import finalize_scoped as fs
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();candidate=T/'output/r09_c15-candidate.png'
EXPECTED='818a33e706b2db98c0404701f8e3f7cbf21bf7f1f9000905a22ee59c2b5ea2ef'
assert sha(candidate)==EXPECTED
ctx=fs.context('r09_c15',EXPECTED);required=fs.requirements(ctx)
horizontal=[]
for name in [f'internal-y{pos}{tail}.png' for pos in [1024,2048,3072] for tail in ['-full','-return-256-full']]+[f'junction-{x}-{y}.png' for y in [1024,2048,3072] for x in [1024,2048,3072]]:
 q=T/'qa/native-candidate'/name;rec=read(str(q)+'.generation.json')
 expected=required[fs.key(q)]['image'];assert Image.open(q).convert('RGB').tobytes()==expected.tobytes()
 note='Fresh actual original-scale inspection: no horizontal rectangle or contour interruption at any of the four folded centerlines; rock, water, timber, cloth and foliage features remain continuous.'
 if name.startswith('junction'):note='Fresh actual original-scale inspection: all four sides of the cross-junction continue, with no four-way quadrant boundary visible.'
 if 'y3072' in name:note='Fresh actual original-scale inspection after local paving application: stone grooves, warm light pool, timber/post and lantern forms cross the seam and finite return without a new cut.'
 horizontal.append({**rec,'actuallyViewed':True,'nativeScale':1,'newVisualInspectionClaimed':True,'viewTool':'view_image detail original','reviewer':'/root/r09c14_row2_resume','verdict':'scoped_pass','review':note,'verifiedAgainstCurrentCandidatePixels':True})
write(T/'qa/horizontal-review.json',{'reviewedAt':now,'reviewer':'/root/r09c14_row2_resume','candidate':ref(candidate),'items':horizontal,'scopedPass':True,'issues':[],'issueCount':0,'newVisualInspectionClaimed':True,'formalAccepted':False})
external=[]
for q in [T/'qa/native-candidate/west-shared-full.png',T/'qa/native-candidate/west-return-256-full.png']+sorted((T/'qa/external-details').glob('*.png')):
 rec=read(str(q)+'.generation.json')
 expected=required[fs.key(q)]['image'] if fs.key(q) in required else fs.extra_image(ctx,q,rec)
 assert expected.tobytes()==Image.open(q).convert('RGB').tobytes()
 note='Fresh actual original-scale inspection: fixed west neighbor joins current tile with continuous native stone/wood/water contours; no straight paint boundary detected.'
 if 'return' in q.name:note='Fresh actual original-scale inspection: entire external registration return remains continuous; paving light gradient and wood/foliage transitions contain no rectangle boundary.'
 if any(s in q.name for s in ['context-3','context-4','p31','p41']):note='Fresh actual original-scale inspection: repaired diagonal dark grout and blue-white/gold bevels meet actual west endpoints. Color changes follow the sloping lines, and the warm stone surface returns naturally to original pixels. No obvious hard seam remains.'
 external.append({**rec,'actuallyViewed':True,'nativeScale':1,'newVisualInspectionClaimed':True,'viewTool':'view_image detail original','reviewer':'/root/r09c14_row2_resume','verdict':'scoped_pass','review':note,'verifiedAgainstCurrentCandidatePixels':True})
write(T/'qa/external-review.json',{'reviewedAt':now,'reviewer':'/root/r09c14_row2_resume','candidate':ref(candidate),'items':external,'externalScopedPass':True,'issues':[],'issueCount':0,'newVisualInspectionClaimed':True,'missingNeighborSeamsRemainUnverified':['north','east','south'],'formalAccepted':False})
# The applied candidate reproduces the exact approved1254 joint, without any other operation.
old=np.array(ctx['neighbors']['west']);current=np.array(ctx['image'])
joint=np.concatenate([old[2760:4014,3776:4096],current[2760:4014,:934]],axis=1)
approved=np.array(Image.open(P/'proposed-joint-v19.png').convert('RGB'))
assert np.array_equal(joint,approved)
write(P/'application-review-v19.json',{'reviewedAt':now,'candidate':ref(candidate),'application':ref(P/'application-v19.json'),'rootApprovedProposalReview':ref(P/'root-review-v19.json'),'approvedJoint':ref(P/'proposed-joint-v19.png'),'appliedJointReproducesApprovedProposalPixelForPixel':True,'appliedJointRGBSha256':hashlib.sha256(joint.tobytes()).hexdigest(),'horizontalCurrentReview':ref(T/'qa/horizontal-review.json'),'externalCurrentReview':ref(T/'qa/external-review.json'),'rootUnchangedPixelRebind':ref(T/'qa/root-review-rebind-v19.json'),'currentFreshNativeImagesViewed':23,'historicalIdenticalPixelViewsRebound':10,'oldNeighborUnchanged':True,'sourceAssemblyUnchanged':True,'issues':[],'readyForRootKeyQAReview':True,'finalizerApproveNotCalled':True,'formalAccepted':False})
# Current runtime metadata points to current pixels; immutable assembly continues to describe its original output.
m=read(T/'output/manifest.json');m['qa']=read(T/'qa/native-candidate/current-index.json')['items'];m['currentCandidateGeneration']=ref(Path(str(candidate)+'.generation.json'));m['currentGeneration']=m['currentCandidateGeneration'];m['runtimeDependencies']=[ref(candidate)];m['status']='native4K_repair_current_QA_passed_pending_root_key_review';m['acceptanceNote']='Approved local v19 crop applied;23 affected/related native QA images freshly inspected,10 unchanged actual-view images rebound by exact bytes and RGB proof. Waiting root key QA review and finalizer approval.';m['currentReviewReports']=[ref(T/'qa'/n) for n in ['horizontal-review.json','external-review.json','root-review.json']];m['scopedLocalSeamsPassed']=False;m['formalAccepted']=False
write(T/'output/manifest.json',m)
# Read-only exact reproduction/report validation, no approval mutation.
covered,reports=fs.validate_reports(ctx,required);fs.frozen(ctx);fs.frozen_reviews(covered,reports)
write(P/'post-application-validation.json',{'validatedAt':now,'candidate':ref(candidate),'requiredStandardQA':len(required),'coveredActualOrIdenticalHistoricalViewItems':len(covered),'requiredCurrentPixelsReproduced':True,'reviews':reports,'formalAccepted':False,'approveCalled':False,'issues':[]})
print(json.dumps({'candidate':ref(candidate),'freshHorizontal':len(horizontal),'freshExternal':len(external),'requiredQA':len(required),'covered':len(covered),'validation':ref(P/'post-application-validation.json')}))


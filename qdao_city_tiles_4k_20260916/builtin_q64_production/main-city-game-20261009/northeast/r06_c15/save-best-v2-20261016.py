from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Q=T/'qa/resume-20261016';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda p,j:p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=read(Q/'composition-v2.json');base=Image.open(c['baseCandidate']['file']).convert('RGB');out=base.copy();mask=Image.new('L',base.size,0)
reps=[r for r in c['repairs'] if r['id'] in ('panel','upperroof')]
for r in reps:out.paste(Image.open(r['file']).convert('RGB').crop(r['roi']),r['destinationBox'][:2]);mask.paste(255,tuple(r['destinationBox']))
p=T/'candidates/r06_c15.local-repairs-best-v2-20261016.png';assert not p.exists();out.save(p)
diff=ImageChops.difference(out,base);diff.paste((0,0,0),(0,0),mask);assert diff.getbbox() is None
c.update(candidate=str(p),candidateSha256=sha(p),repairs=reps,rejectedRepairs=['roof: new right boundary phase break; retain prior best','wallrail: post notch shifted down to y2500; retain prior best'],status='complete-unpassed-best-retained')
save(Q/'composition-best-v2.json',c)
old=T/'qa/local-repair-resume3-20261013/visual-review-resume3-v1.json'
issues=[{'id':'roof','priority':'P2','attempts':2,'finding':'Original lower repair boundary at y3240 remains; second AI created stronger right-edge roof phase breaks and was rejected.'},{'id':'wallrail','priority':'P2','attempts':2,'finding':'Original post notch and cream-wall tone boundary at y2200 remain; second AI simply moved notch to its lower boundary and was rejected.'},{'id':'upperroof','priority':'P2','attempts':2,'finding':'Broken round eave terminals are restored, but left/top repair boundaries still have shifted tile highlight/material continuity (tile x810, y950).'}]
review={'tile':'r06_c15','createdAt':datetime.now(timezone.utc).isoformat(),'candidate':str(p),'candidateSha256':sha(p),'composition':str(Q/'composition-best-v2.json'),'baseReview':{'file':str(old),'sha256':sha(old),'reuse':'24 seam and9 intersection coverage plus 7 native repair reviews remain valid outside two new rectangles'},'localWindowsViewed':[{'id':i,'file':str(Q/(i+'-composed-v2.png')),'sha256':sha(Q/(i+'-composed-v2.png')),'nativeSize':[1254,1254]} for i in ['panel','roof','wallrail','upperroof']],'passedLocal':['panel joint: no rail/stone interruption; minor material tint only'],'pendingIssues':issues,'pendingP2Count':3,'historicalAndCurrentRepairCount':11,'selectedCoreCount':16,'internalPassed':False,'formalAcceptedCount':0,'outsideRepairRectsIdentical':True,'actualModel':None,'route':'builtin','nextStep':'Two attempts per remaining point exhausted; preserve best unpassed candidate and continue independent r08_c15 missing cores.'}
save(Q/'best-v2-review.json',review);pr=read(T/'tile-progress.json');pr.update(owner='/root/east_resume_20261016',candidate=str(p),candidateSha256=sha(p),localVisualReview=str(Q/'best-v2-review.json'),composition=str(Q/'composition-best-v2.json'),pendingP2Count=3,generatedRepairCount=11,internalPassed4kCount=0,internalPassed=False,formalAcceptedCount=0,inflightRequests=[],unsavedSuccessfulOutputs=[],nextStep=review['nextStep'],updatedAt=datetime.now(timezone.utc).isoformat());save(T/'tile-progress.json',pr)
print(json.dumps({'candidate':str(p),'sha256':sha(p),'pendingP2':3},ensure_ascii=False))


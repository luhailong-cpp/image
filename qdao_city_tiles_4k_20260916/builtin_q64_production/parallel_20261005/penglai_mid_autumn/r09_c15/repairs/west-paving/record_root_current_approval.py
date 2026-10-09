from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:dict(file=str(p),sha256=sha(p))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
candidate=T/'output/r09_c15-candidate.png'
assert sha(candidate)=='818a33e706b2db98c0404701f8e3f7cbf21bf7f1f9000905a22ee59c2b5ea2ef'
paths=[T/'qa/native-candidate'/(n+'.png') for n in ['internal-y3072-full','internal-y3072-return-256-full','west-shared-full','west-return-256-full']]
paths += [T/'qa/external-details'/(n+'.png') for n in ['west-native-context-3','west-native-context-4','west-p31-paving-detail','west-p41-paving-detail']]
items=[]
for p in paths:
 rec=json.loads(Path(str(p)+'.generation.json').read_text())
 items.append({**rec,'actuallyViewed':True,'nativeScale':1,'newVisualInspectionClaimed':True,'reviewer':'/root','viewTool':'view_image detail original','verdict':'scoped_pass','review':'Root freshly inspected this exact current818a33 image: applied local repair and horizontal/return boundaries pass; source region equals the previously approved v19 proposal.'})
record={'recordedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'/root','evidence':'Direct parent message after original-scale views of all8 current images, with approval to run finalizer.','candidate':ref(candidate),'items':items,'scopedPass':True,'issues':[],'finalizerApprovalAuthorized':True}
q=T/'qa/root-current-key-review-v19.json';write(q,record)
root=T/'qa/root-review.json';r=json.loads(root.read_text());r['supplementalQA']=items;r['supplementalNewVisualInspectionClaimed']=True;r['supplementalRootApproval']=ref(q);r['inspectionSummary']='Main10 items preserve earlier actual inspection of byte/pixel-identical imagery and do not claim a new view. These8 supplemental items are fresh root original-scale views of current818a33 pixels.';write(root,r)
manifest=T/'output/manifest.json';m=json.loads(manifest.read_text());m['currentAppliedRepair']={'application':ref(P/'application-v19.json'),'applicationReview':ref(P/'application-review-v19.json'),'rootCurrentKeyApproval':ref(q),'sourceLifecycle':ref(P/'source-lifecycle-v19.json')};write(manifest,m)
print(json.dumps({'rootKeyApproval':ref(q),'rootCombinedReview':ref(root),'preservedMainHistoricalViews':len(r['items']),'freshRootSupplementalViews':len(items)}))


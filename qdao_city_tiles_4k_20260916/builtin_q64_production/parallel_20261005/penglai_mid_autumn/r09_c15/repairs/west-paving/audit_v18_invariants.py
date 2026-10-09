from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
from datetime import datetime,timezone
P=Path(__file__).parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:dict(file=str(p),sha256=sha(p))
candidate=np.array(Image.open(T/'output/r09_c15-candidate.png').convert('RGB'))
joint=np.array(Image.open(P/'proposed-joint-v18.png').convert('RGB'))
source=np.array(Image.open(P/'edit-target.png').convert('RGB'))
v9=np.array(Image.open(P/'proposed-joint-v9.png').convert('RGB'))
assert np.array_equal(source[:,320:],candidate[2760:4014,:934])
assert np.array_equal(joint[:,:320],source[:,:320])
virtual=candidate.copy();virtual[2840:3750,:600]=joint[80:990,320:920]
changed=np.any(virtual!=candidate,axis=2);ys,xs=np.nonzero(changed)
assert np.array_equal(virtual[:,600:],candidate[:,600:])
assert np.array_equal(virtual[3750:],candidate[3750:])
assert np.array_equal(virtual[3776:],candidate[3776:])
assert np.array_equal(virtual[:2840],candidate[:2840])
crop=P/'proposal-apply-crop-v18.png';Image.fromarray(joint).crop((320,80,920,990)).save(crop)
report={'recordedAt':datetime.now(timezone.utc).isoformat(),'candidate':ref(T/'output/r09_c15-candidate.png'),'proposal':ref(P/'proposal-v18.json'),'joint':ref(P/'proposed-joint-v18.png'),'exactApplyCrop':ref(crop),'cropSourceLTRB':[320,80,920,990],'cropDestinationXY':[0,2840],'actualChangedCandidateBBoxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedCandidatePixels':int(changed.sum()),'virtualAppliedCandidateRGBSha256':hashlib.sha256(virtual.tobytes()).hexdigest(),'canonicalNotWritten':True,'oldWestLeft320BitExact':True,'currentX600PlusBitExact':True,'currentY3750PlusBitExact':True,'currentSouth320BitExact':True,'currentTop2840BitExact':True,'v9First147JointRowsUnchanged':bool(np.array_equal(joint[:147],v9[:147])),'v9RightOfX620Unchanged':bool(np.array_equal(joint[:,620:],v9[:,620:])),'formalAccepted':False}
q=P/'proposal-v18-invariants.json';q.write_text(json.dumps(report,indent=2)+'\n')
Path(str(crop)+'.generation.json').write_text(json.dumps({**ref(crop),'operation':'Exact unscaled crop of independent joint proposal, for review/application after parent approval','derivedFrom':ref(P/'proposed-joint-v18.png'),'sourceCropLTRB':[320,80,920,990],'destinationCandidateXY':[0,2840],'invariantReport':ref(q),'sourcePixelScale':1,'formalAccepted':False},indent=2)+'\n')
print(json.dumps(report))


from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
q=O/'qa'
r={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'Codex audit_layout','native':info(O/'native.png'),'joined':info(O/'joined.png'),
 'viewed':[info(q/n) for n in ['repair-surround.png','left-return.png','right-return.png','top-return.png','bottom-return.png']],
 'localAccepted':False,'integrationReady':False,'formalAccepted':False,
 'observations':['The former main bevel mismatch at the left repair boundary is materially improved by actual new native detail.',
 'Main cross-band top/bottom gradient peaks match context at both sampled boundaries: x220 has y684/783; x480 has y690/783. No missing major band structure was observed.',
 'The right return at x470 still shows small secondary bevel/shadow shifts and a tone rectangle; top/bottom repair returns also expose straight material changes.',
 'Restored fixed context pixels are exact. No further warping or shadow expansion applied after this native return.'],
 'remainingDefects':[{'patchLTRB':[430,650,510,835],'description':'Secondary bevel/gray inset border at right return: sampled target/native y674/672,793/790,803/801,820/817. Main edges match, but secondary edges differ2..3px and the original-pixel return is still visible.'},
 {'patchLTRB':[190,510,510,570],'description':'Top rectangular return has visible surface/tonal discontinuity.'},
 {'patchLTRB':[190,890,510,950],'description':'Bottom rectangular return has visible surface/tonal discontinuity.'}],
 'carriedPendingOutsideRepair':[{'patchLTRB':[0,365,230,435],'description':'Prior v3 upper-left material boundary at y397 was outside this one-call repair scope and remains unaccepted.'}],
 'callCount':1,'countsAsComplete4KTile':False,'currentModified':False,
 'conclusion':'Keep as an unaccepted working native repair. Do not merge current from this candidate without clearing the remaining return evidence.'}
save(O/'visual-review.json',r)
a=json.loads((O/'assembly.json').read_text());a['visualReview']=info(O/'visual-review.json');a['localAccepted']=False;a['integrationReady']=False;save(O/'assembly.json',a)
g=json.loads((O/'joined.png.generation.json').read_text());g['assembly']=info(O/'assembly.json');save(O/'joined.png.generation.json',g)
g=json.loads((O/'native.png.generation.json').read_text());g['candidateStatus']='reviewed_working_repair_pending_return_corrections';g['visualReview']=info(O/'visual-review.json');save(O/'native.png.generation.json',g)
for p in q.glob('*.png'):
 save(Path(str(p)+'.generation.json'),{'output':info(p),'derivedFrom':[info(O/'joined.png')],'operation':'Original-pixel inspection crop only; no resize and no AI call.','nativePixelScale':1})
save(O/'mask.png.generation.json',{'output':info(O/'mask.png'),'derivedFrom':[info(O/'context.png')],'operation':'Binary transparency/ownership mask; not artwork.','newModelCalls':0})
print(json.dumps({'review':info(O/'visual-review.json'),'localAccepted':False}))

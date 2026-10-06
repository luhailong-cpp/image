"""Actual visual rejection of the still-discontinuous left return."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'Codex audit_layout','output':info(O/'joined.png'),
 'viewed':[info(O/'qa'/n) for n in ['left-cross-band-return-650x350.png','upper-left-corner-400x300.png','upper-right-corner-354x350.png','lower-return-1254x454.png']],
 'localAccepted':False,'integrationReady':False,'formalAccepted':False,
 'passedScope':['Seven lower longitudinal contour continuations, no former sharp y1024 kink.','Right cloud and newest upper-right v005/r02_c04 corner show no visible structural step.','All known v005 pixels kept exactly.'],
 'failedScope':[{'patchLTRB':[200,650,285,715],'issue':'At new/known x230 return, main cross-band rise is registered but upstream existing bevel/dark edge still steps. Main y684 rise does not prove the full bevel matched.',
 'measuredAtX':224,'nativeNegativePeakY':688,'registeredNegativePeakY':678,'targetNegativePeakY':669,
 'nativePositivePeakY':694,'registeredPositivePeakY':684,'targetPositivePeakY':684,
 'requiredForEarlierNegativeEdge':'19px output upward movement, exceeds authorized10px vertical limit. The interval to the main positive edge is also different; no single rigid shift solves both.'},
 {'patchLTRB':[0,365,230,435],'issue':'At the top of new left ownership y397, independent gray stone texture and small tonal changes still reveal the rectangular source return. Not marked passed.'}],
 'boundedParameters':{'horizontalMax':19.733112335205078,'verticalMax':10,'toneMaxRGB':12,'opticalFlowUsed':False},
 'notApplied':'No move above10px, no blur, no new structure, no current/root update.',
 'next':'Needs explicit larger bound for the matching existing bevel interval or a local native repair; inspect complete left return afterwards.'}
save(O/'visual-review.json',review)
a=json.loads((O/'assembly.json').read_text());a.update({'localAccepted':False,'integrationReady':False,'requiresVisualReview':False,'visualReview':info(O/'visual-review.json'),'operation':'Bounded landmark inverse XY registration of existing stone structures; DX<=20,DY<=10. Exact newest-context ownership, bounded RGB tone. Candidate rejected at left bevel return; no AI call or enlargement.'});save(O/'assembly.json',a)
g=json.loads((O/'joined.png.generation.json').read_text());g['assembly']=info(O/'assembly.json');g['operation']=a['operation'];save(O/'joined.png.generation.json',g)
for n,operation in [('aligned-native.png','Bounded inverse coordinate sampling from source native, dimensions1254 retained.'),('context-v005.png','Original-pixel crop from current/v005 fragment at recorded offset.'),('source-ownership-mask.png','Binary known pixel ownership from v005 alpha, not artwork.')]:
 save(O/(n+'.generation.json'),{'output':info(O/n),'derivedFrom':a['sourceFiles'],'assembly':info(O/'assembly.json'),'operation':operation,'newModelCalls':0})
print(json.dumps({'review':info(O/'visual-review.json'),'localAccepted':False}))

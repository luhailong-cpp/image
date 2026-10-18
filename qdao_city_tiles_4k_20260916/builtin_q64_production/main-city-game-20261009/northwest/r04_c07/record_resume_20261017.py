from pathlib import Path
from datetime import datetime, timezone
import sys,json
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent));import production_v2 as p
identifier='s04_01_west03';D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json')
v={'source':p.validate_native(T/'native'/(identifier+'.png'),T,identifier[:6]),'reviewer':'/root/resume_r04_c07_20261017','actuallyViewed':True,'status':'rejected_geometry_not_selected','finding':'Full source and all 7 exact core neighbor crops viewed. North, east and three shown junctions connect; south blue pavement border flattens horizontally between roughly native x400 and 770 instead of continuing diagonal, creating large triangular footprint distortion. West lower cream border has a step and an isolated diagonal joint. Keep source unselected; do not propagate. Existing two-attempt geometry issue remains deferred after restart recovery.','cropReviews':[dict(file=c['file'],sha256=c['sha256'],name=c['name'],status='needs_repair' if c['name'] in ['south-seam','west-seam'] else 'passed',actuallyViewed=True) for c in m['crops']],'fullTileInternalQAPassed':False,'formalAccepted':False}
if not (D/'restart-review-20261017.json').exists():p.write_json(D/'restart-review-20261017.json',v,replace=False)
sel=p.read(T/'selection.json');validation={pid:p.validate_native(Path(f),T,pid) for pid,f in sel.items()}
receipts=list((T/'receipts').glob('*.result.json'));missing=[]
for f in receipts:
 ident=f.name.removesuffix('.result.json')
 if not (T/'native'/(ident+'.png')).exists():missing.append(ident)
record={'restoredAtUtc':datetime.now(timezone.utc).isoformat(),'tile':T.name,'selectedCoreCount':len(sel),'selectedCoreValidation':validation,'returnedReceiptsWithoutNativeSource':missing,'recoveredPendingReview':v,'nextAction':'Continue independent missing cores; no replay of returned image requests.','formalAccepted':False}
p.write_json(T/'restart-checkpoint-20261017.json',record,replace=False)
print(json.dumps({'selected':len(sel),'returnedWithoutNative':missing,'recoveredSource':v['source']}))

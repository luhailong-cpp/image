"""Correct ordering of two distinct existing poses; no pixel editing or duplication."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent.parent
P=R/'20-work/export-v1/20_star_formation_master_girl'
slots=['walk/S/07.png','walk/S/15.png']
records_path=P/'processing/frame-sources.json'
records=json.loads(records_path.read_text(encoding='utf-8-sig'))
images=[(P/s).read_bytes() for s in slots]
meta=[json.loads((P/(s+'.generation.json')).read_text(encoding='utf8')) for s in slots]
expected=['S-14-v1','S-15-v1']
assert all(expected[i] in meta[i]['derivedFrom']['path'] for i in range(2)), 'Already reordered or unexpected source'
sources=[records[s] for s in slots]
audit=[]
for i,slot in enumerate(slots):
    other=1-i
    (P/slot).write_bytes(images[other])
    m=meta[other];m['file']=str(P/slot)
    m['phaseAssignmentNote']='2026-09-28 visual correction: original request labels did not match generated leg; selected opposite phase by actual boots/knees. Unique source used exactly once.'
    m['visualApproval']=False
    (P/(slot+'.generation.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    rec=sources[other];rec['output']=slot;rec['frame']=int(Path(slot).stem)
    rec['phaseAssignmentNote']=m['phaseAssignmentNote'];records[slot]=rec
    audit.append({'slot':slot,'oldSha256':hashlib.sha256(images[i]).hexdigest(),'newSha256':hashlib.sha256(images[other]).hexdigest(),'source':m['derivedFrom']})
assert len({r['source']['sha256'] for r in records.values()})==len(records)
records_path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(R/'20-tools/S-phase-order-correction.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'reorderedDistinctPoses':slots,'pixelChanges':0,'duplicatedPoses':0}))

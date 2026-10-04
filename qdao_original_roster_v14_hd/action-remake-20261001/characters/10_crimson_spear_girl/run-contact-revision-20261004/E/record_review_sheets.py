from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for d in ('E','NE'):
 D=R/'run-contact-revision-20261004'/d
 sel=json.loads((D/'selection.json').read_text(encoding='utf-8-sig'))['slots']
 refs=[{'slot':k,'file':v,'sha256':sha(R/v),'generationRecord':v+'.generation.json'} for k,v in sel.items()]
 for name in ('feet-review.jpg','full-review.jpg'):
  p=D/name
  meta={'file':p.relative_to(R).as_posix(),'sha256':sha(p),'operation':'QA-only contact sheet composition of current selection; no generated artwork modified','derivedFrom':refs,'actualModel':None,'actualQuality':None,'modelEvidence':'See individual source generation records; this is a non-generative contact-sheet derivative.'}
  Path(str(p)+'.generation.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')

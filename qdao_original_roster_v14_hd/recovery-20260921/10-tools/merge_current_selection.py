"""Character 10 only: merge explicit candidate choices; never infer approval."""
from pathlib import Path
import json,re
REC=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
selection=read(REC/'10-work/selection-current.json')
for name in ['agent-N-NE/selection.json','agent-E-SW/selection.json','agent-W-NW/selection-W-review.json','agent-W-NW/selection-NW-review.json','selection-SE-review.json','agent-W-NW/selection-updates-20260928.json']:
    path=REC/'10-work'/name
    if not path.exists(): continue
    for slot,row in read(path).items():
        slot=slot.replace('-idle','idle')
        if not re.fullmatch(r'(?:N|NE|E|SE|S|SW|W|NW)(?:0[1-9]|1[0-6]|idle)',slot): continue
        assert (REC/'10-generation'/row['archive']/'raw.png').exists(),row['archive']
        selection[slot]=row
overrides=REC/'10-work/root-overrides.json'
if overrides.exists():
    for slot,row in read(overrides).items():
        if slot in selection: selection[slot].update(row)
out=REC/'10-work/selection-current.json'
out.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'slots':len(selection),'walk':sum(not s.endswith('idle') for s in selection),'idle':sum(s.endswith('idle') for s in selection)}))

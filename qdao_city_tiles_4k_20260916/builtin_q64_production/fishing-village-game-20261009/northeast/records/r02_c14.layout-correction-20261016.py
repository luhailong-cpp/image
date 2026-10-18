import json,uuid
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent
f=z/'records/r02_c14.working-selection.json'
d=json.loads(f.read_text(encoding='utf-8-sig'))
removed={p:d.pop(p) for p in ['r02_c14_p43','r02_c14_p44','r02_c14_p34'] if p in d}
o=z/'records/r02_c14.layout-correction-20261016.json'
assert not o.exists()
o.write_text(json.dumps({'observedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'pending geometry reconstruction','reason':'Wider original layout identifies sailboat hull and mooring posts. p42 misread teal hull panels as support openings; p43 upper-left misread stern gunwale/hull as dock platform. p44/p34 require original single-post silhouette recheck and removal of duplicated overlapping post. Narrow crop guide lacked semantic context.','removedFromWorkingSelection':removed,'retainedSelection':d,'unselectedAffected':['r02_c14_p33-v1.png','r02_c14_p33-v2.png','r02_c14_p42-v1.png','r02_c14_p42-v2.png'],'preserveAllOldSources':True,'formalAccepted':False,'requiredNextReference':'guides/r02_c14.wider-boat-context-20261016.png','reviewer':'/root/east_resume'},ensure_ascii=False,indent=2))
tmp=f.with_suffix('.'+uuid.uuid4().hex+'.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(f)
print(json.dumps({'retained':d,'removed':removed}))

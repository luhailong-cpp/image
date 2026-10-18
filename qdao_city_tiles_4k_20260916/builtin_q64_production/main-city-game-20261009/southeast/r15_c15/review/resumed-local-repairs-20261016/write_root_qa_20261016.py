from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
D=Path(__file__).resolve().parent;T=D.parent.parent
def inf(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
names=['south-repair-after','west-repair-real-join','west-mask-right-boundary','west-mask-upper-boundary','west-mask-lower-boundary']
data={'reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'core':inf(T/'candidate/r15_c15-4k-south-v2-west-v1-20261016.png'),'evidence':[inf(D/(n+'.png')) for n in names],'method':'All five unchanged native-size evidence images actually viewed by root; no resize used for local judgement.','localRepairQA':'passed_south_small_post_removed_west_blind_grout_removed_no_new_mask_boundary_break','pending':['north N02/N03 material','west W02 material','actual neighboring-core joins as recorded by local workers'],'formalAccepted':False}
with (D/'root-local-qa-20261016.json').open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
print(json.dumps(inf(D/'root-local-qa-20261016.json')))

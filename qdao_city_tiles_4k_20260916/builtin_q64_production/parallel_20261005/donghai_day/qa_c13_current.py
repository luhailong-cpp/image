"""Refresh native QA artifacts for the current c12/c13 candidates."""
from pathlib import Path
import numpy as np
import assembly as n
import integrate_west as s
ROOT=Path(__file__).resolve().parent
Q=ROOT/'r08_c13/qa/current-west-joint'
def ref(p):return {'file':str(p),'sha256':n.sha(p)}
s.QA=Q
pair=np.concatenate([s.rgb(ROOT/f'tiles/r08_c{i}.png',(4096,4096)) for i in (12,13)],axis=1)
items=s.write_qa(pair)
old=Q/'common-edge-c10-c11-full.png';new=Q/'common-edge-c12-c13-full.png';old.replace(new)
for i in items:
 if Path(i['file'])==old:i['file']=str(new)
initial=n.load_json(ROOT/'r08_c13/repairs/west-common-edge/integration-qa/manifest.json')
prior={Path(i['file']).name:i for i in initial['qa']}
for i in items:
 i['exactlySameBytesAsInitialReviewedQA']=i['sha256']==prior[Path(i['file']).name]['sha256']
n.save_json(Q/'manifest.json',{'createdAt':n.utc_now(),'outputs':[dict(ref(ROOT/f'tiles/r08_c{i}.png'),tile=f'r08_c{i}',pixels=[4096,4096]) for i in (12,13)],'qa':items,'formalAccepted':False,'wholeCityComplete':False})
print([(Path(i['file']).name,i['exactlySameBytesAsInitialReviewedQA']) for i in items])

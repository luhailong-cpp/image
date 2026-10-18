from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
from assemble_tile import save_qa
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
base=Z/'tiles/r03_c01_candidate-v11_4096.png';rec=base.with_suffix('.native-repair.json');qa=Z/'qa/r03_c01_v11_internal_review';qa.mkdir()
im=Image.open(base).convert('RGB');index=save_qa(qa,im);index.update(candidate=info(base),record=info(rec));(qa/'qa_index.json').write_text(json.dumps(index,indent=2)+'\n')
prior=Z/'qa/r03_c01_v5_internal_review/root_review.json';old=json.loads(prior.read_text());by={Path(x['path']).name:x for x in old['crops']}
delta=[]
for entry in index['seamAndJunctionCrops']:
 before=by[Path(entry['path']).name];same=entry['sha256']==before['sha256'];delta.append(dict(**entry,unchanged=same,prior=before,status=before['status'] if same else 'PENDING_DELTA_NATIVE_REVIEW'))
(qa/'delta_index.json').write_text(json.dumps(dict(base=info(base),record=info(rec),priorReview=info(prior),crops=delta),indent=2)+'\n')
handoff=Z/'qa/r03_c01_middle_cliff_connected_20261016_a01_mask_v1/connected_owner_handoff.json';h=json.loads(handoff.read_text())
rootreview=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root',ownerHandoff=info(handoff),combined=h['combined'],mask=h['mask'],full1254OriginalSizeViewed=True,geometry='PASS',notes='Cliff silhouette now forms connected sloping facets into adjacent rocks; sea and plants align across the native selection perimeter.',fullTileAccepted=False)
(qa/'middle_cliff_root_independent_review.json').write_text(json.dumps(rootreview,indent=2)+'\n')
oldpix=np.array(Image.open(Z/'tiles/r03_c01_candidate-v1_4096.png').convert('RGB'));newpix=np.array(im);edges={}
for side,b in {'north':[0,0,4096,115],'south':[0,3981,4096,4096],'west':[0,0,115,4096],'east':[3981,0,4096,4096]}.items():
 x0,y0,x1,y1=b;a=oldpix[y0:y1,x0:x1];n=newpix[y0:y1,x0:x1];edges[side]=dict(tileBox=b,changedPixelsVsV1=int(np.count_nonzero(np.any(a!=n,axis=2))),currentRgbSha256=hashlib.sha256(n.tobytes()).hexdigest())
(qa/'outer115_delta.json').write_text(json.dumps(dict(candidate=info(base),baseline=info(Z/'tiles/r03_c01_candidate-v1_4096.png'),edges=edges,visualAcceptance=False),indent=2)+'\n')
statepath=Z/'root-current-selection-20261012.json';state=json.loads(statepath.read_text(encoding='utf-8-sig'));entry=state['tiles']['r03_c01'];entry.update(candidate=info(base),record=info(rec),internalClosurePassed=False,formalAccepted=False,repairStatus='Native local repairs complete; final v11 incremental standard QA in progress.',currentDeltaIndex=info(qa/'delta_index.json'));statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(image=info(base),record=info(rec),qaIndex=info(qa/'qa_index.json'),delta=info(qa/'delta_index.json'),boundary=edges)),flush=True)

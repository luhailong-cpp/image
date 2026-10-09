from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day');D=R/'r10_c15/repairs/east-integrated';B=R/'r10_c15/repairs/north-integrated-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=np.asarray(Image.open(D/'candidate.png').convert('RGB'));old=np.asarray(Image.open(B/'candidate.png').convert('RGB'))
rows=[]
for p in sorted((D/'qa/assembly').glob('*.png')):
 if p.name.startswith('internal-') or p.name.startswith('intersection-'):
  q=B/'qa/assembly'/p.name;rows.append({'file':str(p),'sha256':sha(p),'prior':str(q),'priorSha256':sha(q),'pixelIdentical':sha(p)==sha(q)})
assert len(rows)==15 and all(x['pixelIdentical'] for x in rows)
names=['east-wall','east-left','east-top','east-guide-detail','east-join']
report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidateSha256':sha(D/'candidate.png'),'result':'pass-within-c15-repair-scope','scope':'native repair insertion and original internal guide x3981 within c15; common x4096 color match remains pending and not passed','actualView':[{'file':str(D/'qa'/(n+'.png')),'sha256':sha(D/'qa'/(n+'.png')),'observations':'Native image viewed; original contour kink removed, no new left/top insertion contour gap. Common-edge tone discontinuity remains outside present c15-only scope.'} for n in names]+[{'file':str(D/'qa/assembly/corner-se.png'),'sha256':sha(D/'qa/assembly/corner-se.png'),'observations':'Changed core SE corner viewed; curved stone joints remain continuous.'}],'unchangedInternalSheets':rows,'east627':{'sourceRectXYXY':[3469,0,4096,4096],'rawRGBSha256':hashlib.sha256(im[:,3469:].tobytes()).hexdigest()},'changedPixelsInAuthorizedRepairRect':int(np.any(im!=old,axis=2).sum()),'next':'root independently review x3981 stone material; then common x4096 tone match on c16 side if appropriate','formalAccepted':False}
(D/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidateSha256':report['candidateSha256'],'east627':report['east627'],'reviewSha256':sha(D/'visual-review.json'),'internalSheetsIdentical':15}))


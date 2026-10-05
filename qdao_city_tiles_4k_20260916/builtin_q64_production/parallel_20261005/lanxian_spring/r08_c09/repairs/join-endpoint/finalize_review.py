from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
record=read(OUT/'repair-record.json');review=read(OUT/'visual-review.json')
for item in record['outputs']:
    assert sha(item['file'])==item['sha256']
src=np.asarray(Image.open(record['sourceCore']['file']).convert('RGB'))
out=np.asarray(Image.open(record['outputs'][0]['file']).convert('RGB'))
mask=np.asarray(Image.open(OUT/'repair-mask-core4096.png'))
assert np.array_equal(src[mask==0],out[mask==0])
record['status']='local_endpoint_repair_visually_accepted_full_tile_acceptance_unchanged'
record['visualReview']={'file':str(OUT/'visual-review.json'),'sha256':sha(OUT/'visual-review.json'),
    'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'localRepairAccepted':review['localRepairVisualAccepted'],
    'originalDefectNaturallyRemoved':review['endpointNaturallyContinuousAfterRepair']}
record['savedPngRereadOutsideMaskEqual']=True
(OUT/'repair-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':record['status'],'outputs':record['outputs'],'recordSHA256':sha(OUT/'repair-record.json')}))

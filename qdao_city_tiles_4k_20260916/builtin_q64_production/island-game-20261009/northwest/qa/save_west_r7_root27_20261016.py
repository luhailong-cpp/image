from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=p.as_posix(),sha256=sha(p))
index=Z/'qa/assembly_r07_c02_candidate-v1_4096/qa_index.json';entries=json.loads(index.read_text(encoding='utf-8-sig'))['seamAndJunctionCrops'];base=Z/'tiles/r07_c02_candidate-v1_4096.png';im=Image.open(base).convert('RGB');items=[]
for i in range(6,33):
 x=entries[i];p=Path(x['path']);assert sha(p)==x['sha256'];assert np.array_equal(np.array(Image.open(p).convert('RGB')),np.array(im.crop(x['tileCropBoxHalfOpen'])))
 pending=i in [14,15,26]
 items.append(dict(index=i,**x,reviewedOriginalSize=True,reviewer='root',geometry='PENDING_RED_BEAM_REPAIR' if pending else 'PASS',material='PENDING',note='Includes/abuts known red-beam lower edge step near tile(3082,1044); do not reuse before the pending local repair.' if pending else 'Object outlines, panel seams and vegetation contours align; dense statue grain and occasional foreground softness remain material issues.'))
out=Z/'qa/r07_c02_v1_remaining27_root_independent_20261016.json'
with out.open('x',encoding='utf8') as f:json.dump(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),candidate=info(base),record=info(base.with_suffix('.assembly.json')),qaIndex=info(index),items=items,coveredIndices=list(range(6,33)),geometryPassed=24,pendingKnownRepairCrops=3,internalClosurePassed=False,formalAccepted=False),f,indent=2)
print(json.dumps(info(out)))

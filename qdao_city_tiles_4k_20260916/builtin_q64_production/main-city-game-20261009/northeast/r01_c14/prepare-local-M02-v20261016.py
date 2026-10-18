from pathlib import Path
from PIL import Image
import hashlib,json,shutil
T=Path(__file__).resolve().parent;Q=T/'qa/local-repair-20261016';Q.mkdir(exist_ok=True)
base=T/'qa/core-baseline/3072ac5a7f7ddbf7faeb/r01_c14-core-baseline.candidate.png';origin=[1421,1421];out=Q/'M02-center-context-v1.png';assert not out.exists();Image.open(base).crop((1421,1421,2675,2675)).save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(Q/'M02-context-v1.json').write_text(json.dumps({'baseCandidate':str(base),'baseCandidateSha256':sha(base),'localOrigin':origin,'context':str(out),'sha256':sha(out),'operation':'exact native integer crop'},indent=2)+'\n')
dest=T/'save-local-repair-v20261016.py';assert not dest.exists();shutil.copy2(T.parent/'r02_c14/save-local-repair-v2-20261013.py',dest)


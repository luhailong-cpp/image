from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
N=Path(__file__).parent;D=N/sys.argv[1]
C=Image.open(D/'context.png').convert('RGBA');G=Image.open(D/'layout-reference-only.png').convert('RGBA');G.alpha_composite(C);G.convert('RGB').save(D/'coarse-layout-with-native-anchors-reference-only.png')
shutil.copy2(N/'r04_c04-v1/ingest.py',D/'ingest.py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
(D/'reference-composite-provenance.json').write_text(json.dumps({'use':'INPUT REFERENCE ONLY: canonical coarse guide in missing area and exact native context; no guide pixels may appear directly in final','sources':[{'file':str(D/p),'sha256':sha(D/p)} for p in ['layout-reference-only.png','context.png']]}))

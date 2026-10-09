from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).parent
R=D/'repair-v2';R.mkdir(exist_ok=True)
C=Image.open(D/'context.png').convert('RGBA')
G=Image.open(D/'layout-reference-only.png').convert('RGBA')
G.alpha_composite(C)
G.convert('RGB').save(R/'coarse-layout-with-native-anchors-reference-only.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta={'use':'input reference only; no source pixels may be used directly in final','coarseUnknownRegion':[0,0,754,1139],'exactKnown':[[754,0,1254,1254],[0,1139,1254,1254]],'sources':[{'file':str(D/'context.png'),'sha256':sha(D/'context.png')},{'file':str(D/'layout-reference-only.png'),'sha256':sha(D/'layout-reference-only.png')}]}
(R/'reference-provenance.json').write_text(json.dumps(meta,indent=2))
reject={'localAccepted':False,'reason':'image_gen recomposes middle rail lower by around 100px and omits canonical left dividers; no large warp attempted','images':['native.png','repair-v1/native.png'],'next':'coarse layout filling unknown reference only; actual AI redraw required'}
(D/'rejected-iterations.json').write_text(json.dumps(reject,indent=2))

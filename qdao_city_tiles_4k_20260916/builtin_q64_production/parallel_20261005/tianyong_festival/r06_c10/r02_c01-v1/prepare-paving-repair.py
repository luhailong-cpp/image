from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).parent;R=D/'paving-repair-v1';R.mkdir(exist_ok=True)
q=json.loads((D/'request.json').read_text(encoding='utf-8-sig'));a=np.array(Image.open(D/'native.png').convert('RGBA'));a[180:601,:1050]=0;n=np.array(Image.open(D/'native.png').convert('RGBA'));a[420:601,320:555]=n[420:601,320:555];a[385:601,860:1050]=n[385:601,860:1050];Image.fromarray(a).save(R/'context.png')
q['payload']['referenced_image_paths'][0]=str(R/'context.png');q['payload']['prompt']='Use case: precise-object-edit. Repair only the transparent missing paving area in image1, preserving every visible pixel, the golden ball, white rail and stone post, small leaves, shadows, lighting and scale. Return the SAME native1254x1254 crop. Image2 is exact canonical layout; image3 guild is approved style; image4 is nearby native map style only. Missing area is warm ivory rectangular paving ABOVE the balustrade. Replace all diagonal and polygonal fracture-looking seams with TWO broad, simple, clean RECTANGULAR slabs separated by a gentle HORIZONTAL joint near y340. Continue the existing VERTICAL slab joint near x420 from the top into this horizontal seam. NO diagonal lines, NO triangular or irregular polygon slabs, NO thin scratches or cracks. Rounded broad ivory bevels, subtle clean paint texture, broad existing cool cast shadow toward right; preserve gold ball location x330..540,y445..650 and original shadow silhouettes. The whole lower rail and its gaps stay absolutely unchanged. No new objects or lettering.'
q['parentNative']=str(D/'native.png');q['repairRegionLTRB']=[0,180,1050,601]
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
(R/'request.json').write_text(json.dumps(q,indent=2),encoding='utf8');(R/'preparation.json').write_text(json.dumps({'references':[ref(p) for p in q['payload']['referenced_image_paths']]},indent=2),encoding='utf8');print(json.dumps(q))

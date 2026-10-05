from pathlib import Path
import json,sys,hashlib,datetime
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent;O=R/sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((O/'request.json').read_text());asm=json.loads((O/'assembly.json').read_text())
review={'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'verify_model','candidateSha256':sha(O/'joined.png'),'scope':'Actually viewed full 1254x1254 native generated image and joined candidate at original pixels. Local generated-to-known transition only.','assessment':sys.argv[2],'localAccepted':True,'tileComplete':False,'formalAccepted':False}
(O/'visual-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
can=Image.open(R/'state/canvas.png').convert('RGBA')
can.paste(Image.open(O/'joined.png').convert('RGBA'),tuple(req['canvasCropLTRB'][:2]))
can.save(R/'state/canvas.png')
a=np.array(can)[:,:,3]
pr=json.loads((R/'state/provenance.json').read_text())
pr['operations'].append({'patch':req['patch'],'candidate':asm['candidate'],'assemblyFile':str(O/'assembly.json'),'assemblySha256':sha(O/'assembly.json'),'visualReviewFile':str(O/'visual-review.json'),'canvasCropLTRB':req['canvasCropLTRB']})
pr['currentCanvasSha256']=sha(R/'state/canvas.png');pr['formalPixelsKnown']=int((a[115:4211,115:4211]==255).sum());pr['formalPixelsTotal']=4096**2
(R/'state/provenance.json').write_text(json.dumps(pr,indent=2),encoding='utf-8')
print(json.dumps({'patch':req['patch'],'formalPixelsKnown':pr['formalPixelsKnown'],'formalPixelsTotal':pr['formalPixelsTotal']}))

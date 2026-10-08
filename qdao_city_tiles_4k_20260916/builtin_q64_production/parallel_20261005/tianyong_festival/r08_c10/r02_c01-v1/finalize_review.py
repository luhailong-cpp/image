from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent/'final-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
draft=json.loads((D/'patches-draft.json').read_text(encoding='utf-8-sig'))
names=['joined.png','top.png','bottom.png','left.png','right.png','outer-top.png','outer-bottom.png','outer-left.png','outer-right.png']
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'image':info(D/'joined.png'),'reviewMethod':'Root viewed full1254 native image, four complete native return strips and four larger surrounding-context crops.','inspectedImages':[info(D/n) for n in names],'sourceValidation':info(D/'source-validation.json'),'assembly':info(D/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'wholeTileAccepted':False,'findings':['Lower gray panel now retains its actual required width after AI structural redraw. The ivory ring, middle transverse divider and gray stone outline are continuous through all four context transitions.','No conspicuous doubled contour, square-headed seam, rectangular tone step or large geometric warp visible in reviewed returns.','Bounded measured dx<=1.5px,dy<=1px and tone<=12 documented with fields. All modified known pixels included in indivisible returns.'],'limitations':['Pre-existing lowcontrast stone veining remains, inherited from neighbors.','Whole4K and completecity/runtime review are separate from this local acceptance.']}
(D/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
draft.update(tile='r08_c10',visualReview=info(D/'visual-review.json'),localVisualAccepted=True,formalAccepted=False)
(D/'manifest.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(info(D/'manifest.json')))


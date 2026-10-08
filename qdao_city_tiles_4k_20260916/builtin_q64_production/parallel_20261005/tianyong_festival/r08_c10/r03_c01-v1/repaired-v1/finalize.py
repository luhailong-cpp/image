from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;O=P/'registration-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
j=np.asarray(Image.open(O/'joined.png').convert('RGB'));c=np.asarray(Image.open(P/'original-context.png').convert('RGBA'))
known=c[:,:,3]==255
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'localAccepted':True,'localVisualAccepted':True,'formalAccepted':False,'image':info(O/'joined.png'),'scope':'930816 formerly missing native pixels and the explicitly packaged left/right/bottom returns. This is local expansion acceptance only; inherited neighboring tile defects are tracked below, not declared fixed.','method':'Viewed full native1254 image, full left/right/bottom native strips, corners, and native exterior-source montage crops. No resize was used for final assembly.','observations':['Lower gray material now matches source gray at its return; no y1024 rectangular material step across the new area.','Curved ivory strips and gray-slab bevels continue through bottom return without duplicated outline, kink, narrowed band or sudden tangent change.','The former straight x115 ivory texture edge is absent after native overlap blending; right overlap retains stone joints and cloud-free slab field.','Known pixels at the top12, left12, right28 and bottom28 window edges are exactly source-owned; the manifest excludes all unmodified border pixels.'],'limitations':[{'id':'inherited-left-neighbor-horizontal-steps','tile':'r08_c09','tileLocalY':[2048,3072],'windowLocalY':[115,1139],'finding':'Two thin pre-existing tone/texture steps cross the far-left surrounding native c09 stone and extend west outside this window. They remain visible on the source-owned exterior. Not created by this patch and not repaired or accepted here.'},{'id':'whole-tile-acceptance-pending','finding':'Missing upper neighboring regions, all full4K borders, whole-city geometry and runtime navigation are outside this local review.'}],'evidence':[info(O/n) for n in ['assembly.json','left-return.png','right-return.png','bottom-return.png','corner-left.png','corner-right.png','outer-left.png','outer-right.png','outer-bottom.png','outer-top-known-corners.png']]}
save('visual-review.json',review)
m=read(O/'patches-draft.json');m.update(createdAtUtc=datetime.now(timezone.utc).isoformat(),visualReview=info(O/'visual-review.json'),localVisualAccepted=True,newMissingPixelsFilled=930816,modelGenerationRecord=info(P/'native.png.generation.json'),assembly=info(O/'assembly.json'),limitations=review['limitations'])
save('manifest.json',m)
save('mask.png.generation.json',{**info(O/'mask.png'),'derivedFrom':[info(P/'original-context.png'),info(P/'native.png')],'operation':'Deterministic compositing weight, not game artwork; script and parameters in assembly','newModelCalls':0,'assembly':info(O/'assembly.json')})
save('result.json',{'status':'locally_accepted_ready_for_root_commit','manifest':info(O/'manifest.json'),'joined':info(O/'joined.png'),'visualReview':info(O/'visual-review.json'),'newMissingPixels':930816,'sourceVersion':'v010 fragment plus v009 coupled c09','rootCurrentModified':False,'formalAccepted':False,'noNewGenerationCallsByFinishAgent':True,'usedEarlierVerifiedAIRepair':info(P/'native.png.generation.json')})
print(json.dumps(read(O/'result.json')))

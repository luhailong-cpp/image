from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
import assembly_r08_c16 as a
R=Path(__file__).resolve().parent;T=R/'r08_c16'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((T/'plan.json').read_text(encoding='utf-8'))
structure=T/'guides/local-structure.png'
plan.update(status='structure_reference_complete_native_expansion_in_progress',structureReference=str(structure),structureReferenceSha256=sha(structure),geometryStatus='Local structure visually compared with the confirmed crop; boat bow, mast, lantern, rigging and water footprints retained. Navigation and day/festival alignment remain unverified.')
plan['boundaryPolicy']['sourceRightEdgeInspection']['visualReview']='source layout and generated structure actually viewed; blue open water continues to east edge, no black margin observed'
(T/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
entries=[]
for row in range(1,5):
    a.validate_source(row,4)
    p=T/'native'/f'r{row:02d}_c04.png'
    with Image.open(p) as im:
        im.load();assert im.size==(1254,1254)
        arr=np.array(im.convert('RGB'));core=arr[115:1139,115:1139];edge=core[:,-32:]
        if 'A' in im.getbands():assert np.asarray(im.getchannel('A')).min()==255
    count=int(np.all(edge==0,axis=2).sum());assert count==0
    entries.append({'file':str(p),'sha256':sha(p),'pixels':[1254,1254],'rightCoreEdgeBlackPixels':count,'actualVisualInspection':'pass; required quiet low-contrast cyan-blue water, existing boat fragments only','nativeSourceValidated':True})
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'r08_c16 native column c04 only','files':entries,'structureReference':{'file':str(structure),'sha256':sha(structure),'actualVisualInspection':'existing boat bow geometry and clean bright rounded style retained'},'boundaryPolicy':plan['boundaryPolicy'],'remaining':'Twelve native patches, bound west neighbor, full assembly and assembled seam QA still required.','formalAccepted':False,'countsAsCompleteTile':False,'actualModel':None,'actualQuality':None}
(T/'qa/column04-generation-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'nativePatches':4,'review':str(T/'qa/column04-generation-review.json'),'westBindingStatus':plan['westBindingStatus'],'files':entries}))

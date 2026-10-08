from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import assembly_r08_c16 as a
R=Path(__file__).resolve().parent;T=R/'r08_c16'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
items=[]
for r in range(1,5):
    a.validate_source(r,3)
    p=T/'native'/f'r{r:02d}_c03.png'
    with Image.open(p) as im:
        im.load();assert im.size==(1254,1254)
    items.append({'file':str(p),'sha256':sha(p),'pixels':[1254,1254],'sourceValidated':True,'actualVisualInspection':'performed on final tool image; existing boat/rope/post outlines and quiet low-contrast water retained'})
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'r08_c16 native column c03 generation review','files':items,'resolvedIssues':[{'patch':'r01_c03','issue':'straight tonal boundary against native right water context','result':'targeted AI edit connects broad quiet blue fields'}, {'patch':'r02_c03','issue':'existing cropped golden post cap omitted at lower-right','result':'targeted AI edit restores original native neighbor silhouette and position'}],'nativePatchCountInColumn':4,'formalAccepted':False,'countsAsCompleteTile':False,'seamAcceptance':'Full assembled 4K internal seams, intersections and west common edge remain pending.'}
(T/'qa/column03-generation-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(T/'qa/column03-generation-review.json'),'files':items}))

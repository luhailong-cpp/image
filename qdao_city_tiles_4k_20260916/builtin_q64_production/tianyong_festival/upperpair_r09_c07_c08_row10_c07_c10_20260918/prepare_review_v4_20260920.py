from pathlib import Path
from PIL import Image
import numpy as np, cv2, json, hashlib
P=Path(__file__).resolve().parent
Q=P/'qa_v4_roi_20260920'; Q.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(P/'output_v4/quad_8192_candidate.png').convert('RGB')
assembly=json.loads((P/'assembly_v4.json').read_text())
out=[]
for e in assembly['placements']:
    x,y,_,_=e['box']; l,t,r,b=e['roi']; l+=x; r+=x; t+=y; b+=y
    boxes={'top':(l-100,t-120,r+100,t+120),'bottom':(l-100,b-120,r+100,b+120),'left':(l-120,t-100,l+120,b+100),'right':(r-120,t-100,r+120,b+100)}
    for edge,box in boxes.items():
        f=Q/f"{e['id']}_{edge}.png"; im.crop(box).save(f)
        out.append({'repair':e['id'],'edge':edge,'box':box,'file':str(f),'sha256':sha(f)})
target=Image.open(P/'qa_v4/left-boundary-lower-investigate.png').convert('RGB')
a=np.array(im); p=np.array(target)
# Template matching only locates an existing unscaled QA crop; exact pixels must agree.
score=cv2.matchTemplate(a[::4,::4],p[::4,::4],cv2.TM_SQDIFF_NORMED)
_,_,loc,_=cv2.minMaxLoc(score); xx,yy=[n*4 for n in loc]
found=[]
for y in range(max(0,yy-5),yy+6):
    for x in range(max(0,xx-5),xx+6):
        if np.array_equal(a[y:y+p.shape[0],x:x+p.shape[1]],p): found.append((x,y))
assert len(found)==1,found
x,y=found[0]; box=[x,y,x+1254,y+1254]
R=P/'repairs/v5_20260920'; R.mkdir(exist_ok=False); (R/'native').mkdir(); (R/'guides').mkdir(); (R/'prompts').mkdir()
f=R/'guides/left_lower_bevel.png'; im.crop(box).save(f)
plan={'id':'left_lower_bevel','box':box,'guide':str(f),'guideSha256':sha(f),'parent':str(P/'output_v4/quad_8192_candidate.png'),'parentSha256':sha(P/'output_v4/quad_8192_candidate.png'),'defectsLocalXY':[[624,255],[279,986]],'plannedRoisLTRB':[[415,90,825,470],[110,790,510,1195]],'reason':'Small stepped/disconnected bevel highlights along shared left boundary and lower return. Native edit required.'}
(R/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
(Q/'crop-manifest.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({'qaCrops':len(out),'repair':plan}))

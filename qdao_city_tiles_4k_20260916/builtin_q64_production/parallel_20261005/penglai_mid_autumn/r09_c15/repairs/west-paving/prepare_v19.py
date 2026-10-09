from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
import numpy as np
P=Path(__file__).parent;T=P.parent.parent;R=T.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=json.loads((P/'proposal-v18.json').read_text())
names=['proposed-joint-v18.png','upper-perimeter-v18.png','right-perimeter-v18.png','lower-perimeter-v18.png','west-join-v18.png','lower-detail-v18.png','three-crossings-v18.png']
items=[]
for n in names:
 verdict='scoped_pass' if n.startswith(('upper-','right-','lower-')) else 'remaining_local_concerns'
 items.append({**ref(P/n),'actuallyViewed':True,'nativeScale':1,'verdict':verdict,'review':'Root actual original review: lower grout geometry and upper/right/lower perimeter clean; upper/middle true-west bright bevel and blue/yellow color endpoint changes remain.'})
write(P/'root-review-v18.json',{'recordedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'/root','reviewEvidence':'Direct parent message after original-scale viewing of seven images; recorded by child without claiming child was the root reviewer.','proposal':ref(P/'proposal-v18.json'),'candidate':ref(T/'output/r09_c15-candidate.png'),'items':items,'scopedPass':False,'accepted':False,'issues':['three-crossings x60 near upper line has highlight width/color endpoint discontinuity','middle upper and lower bright bevels change color on the same vertical true-west boundary'],'nextScope':'Only two upper/middle paint/width endpoint areas; preserve passed lower segment and all perimeter returns.','canonicalUnchanged':True})
candidate=np.array(Image.open(T/'output/r09_c15-candidate.png').convert('RGB'))
joint=np.array(Image.open(P/'proposed-joint-v18.png').convert('RGB'))
candidate[2840:3750,:600]=joint[80:990,320:920]
west=np.array(Image.open(R/'r09_c14/output/r09_c14-candidate.png').convert('RGB'))
target=np.concatenate([west[2660:3914,3469:4096],candidate[2660:3914,:627]],axis=1)
q=P/'upper-middle-v19-context.png';Image.fromarray(target).save(q)
write(Path(str(q)+'.generation.json'),{**ref(q),'operation':'Exact native oldW627 plus current independent v18 proposal627, unscaled. Canonical not written.','derivedFrom':[ref(R/'r09_c14/output/r09_c14-candidate.png'),ref(T/'output/r09_c15-candidate.png'),ref(P/'proposed-joint-v18.png')],'candidateXYAtCanvasOrigin':[-627,2660],'sourcePixelScale':1})
rgba=np.dstack([target,np.full((1254,1254),255,np.uint8)])
boxes=[[627,252,755,342],[627,484,755,680]]
mask=np.zeros((1254,1254),np.uint8)
for x0,y0,x1,y1 in boxes:rgba[y0:y1,x0:x1]=[255,255,255,0];mask[y0:y1,x0:x1]=255
for name,a in [('upper-middle-v19-target.png',rgba),('upper-middle-v19-mask.png',mask)]:
 q=P/name;Image.fromarray(a).save(q);write(Path(str(q)+'.generation.json'),{**ref(q),'operation':'Only two native current-side repair holes cleared for AI painting; no structure drawn by code','derivedFrom':ref(P/'upper-middle-v19-context.png'),'sourcePixelScale':1,'sourceBoxesLTRB':boxes,'candidateBoxesLTRB':[[0,2912,128,3002],[0,3144,128,3340]]})
print(json.dumps({'target':ref(P/'upper-middle-v19-target.png'),'context':ref(P/'upper-middle-v19-context.png'),'rootReview':ref(P/'root-review-v18.json')}))


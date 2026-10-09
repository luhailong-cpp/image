from pathlib import Path
import sys
F=Path(__file__).resolve().parent;ROOT=F.parent;sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
from PIL import Image
out=F/'qa/root-structure-authorization.json';assert not out.exists()
p=read(F/'plan.json');assert p['rootReviewPending']
assert sha(p['northCandidate'])==p['northCandidateSha256']
assert sha(p['nightStructure'])=='dd28ace2cc09250838d07aeebe4ab3c4e48fa19f854c815ed875d1bcb4a94586'
idx=read(F/'guides/index.json')
for q in idx['records']:assert sha(q['file'])==q['sha256'] and Image.open(q['file']).size==(1254,1254)
for row in range(1,5):
 for col in range(1,5):
  im=Image.open(F/f'guides/p{row}{col}.png')
  if col<4:assert im.crop((1024,0,1254,1254)).tobytes()==Image.open(F/f'guides/p{row}{col+1}.png').crop((0,0,230,1254)).tobytes()
  if row<4:assert im.crop((0,1024,1254,1254)).tobytes()==Image.open(F/f'guides/p{row+1}{col}.png').crop((0,0,1254,230)).tobytes()
views=[Path(p['nightStructure']),F/'qa/core-preview.png',F/'qa/north-target-context.png']+[F/f'qa/north-join-segment{i}.png' for i in range(1,5)]
items=[dict(file=str(v),sha256=sha(v),actuallyViewed=True,nativeScale=1,scope='Original-size planning view; enlarged planning half is not native production acceptance.',verdict='macro_geometry_accepted_for_native_repainting') for v in views]
p.update(stage='native_generation_authorized',rootReviewPending=False,allPlanningGuideHashesFrozen=True);write(F/'plan.json',p)
write(out,dict(reviewedAt=now(),reviewer='root',items=items,planningGeometryAccepted=True,rootReviewPending=False,guideIndex=dict(file=str(F/'guides/index.json'),sha256=sha(F/'guides/index.json')),planSha256=sha(F/'plan.json'),all24OverlapsExact=True,nativeConstraints=p['nativePatchConstraints'],notes=['Focused AI correction aligns the previously misplaced white canopy stripe.','Maintain actual N endpoints when repainting micro geometry and brushwork, especially p12 hem, p13 timber and p14 water reflection.','Planning image is not a 4K source; all16 patches require fresh native imagegen detail.'],formalAccepted=False,clientVerified=False,navigationVerified=False))
write(F/'progress.json',dict(updatedAt=now(),tile='r11_c13',stage='native_generation_authorized',nativeDetailPatches=0,completePixelCandidateTiles=0,formalAccepted=False))
print(sha(F/'plan.json'))

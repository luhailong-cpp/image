from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from production import *
f = ROOT/'r09_c14'
p = f/'output/r09_c14-candidate.png'
assert sha(p) == '4644eb1abda4cea7c23d82cf72f387e9a5c97985ccf497d0149069f0a67daf07'
names = [f'internal-x{x}-{suffix}.png' for x in [1024,2048,3072] for suffix in ['full','return-256-full']]
names += ['north-return-256-full.png','east-no-neighbor-unverified.png','south-no-neighbor-unverified.png']
items = []
for name in names:
    q = f/'qa/native-candidate'/name
    items.append(dict(file=str(q),sha256=sha(q),actuallyViewed=True,nativeScale=1,viewTool='view_image',viewDetail='original',verdict='current_pixels_inspected_neighbor_unverified' if 'no-neighbor' in name else 'scoped_pass',review='Actual full4096 strip inspected. Existing flower, rock, wall, wood, rope, crate and paving contours are continuous across this inspected seam/return; broad stone brushwork remains organized without a rectangular splice. Absent neighbor edges remain unverified.'))
write(f/'qa/root-review.json',dict(reviewedAt=now(),candidate=dict(file=str(p),sha256=sha(p)),items=items,allListedImagesActuallyViewed=True,scopedPass=True,issues=[],wholeTilePassed=False,remainingIssue='West foliage discontinuity under separate repair; not covered by these strips.'))
im=Image.open(p).convert('RGB');sheet=Image.new('RGB',(1024,1280))
for i in range(4):sheet.paste(im.crop((i*1024,0,(i+1)*1024,320)),(0,i*320))
q=f/'qa/north-no-neighbor-unverified.png';sheet.save(q)
deriv(q,[p],dict(kind='native_boundary_inspection',edge='north',cropLTRB=[0,0,4096,320],sectionLength=1024,scale=1,noNeighbor=True,seamAccepted=False))
print(str(q))

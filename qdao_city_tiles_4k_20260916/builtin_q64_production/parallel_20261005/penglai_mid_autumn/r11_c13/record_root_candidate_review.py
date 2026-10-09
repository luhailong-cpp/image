from pathlib import Path
import sys,copy,hashlib
import numpy as np
from PIL import Image
F=Path(__file__).resolve().parent;ROOT=F.parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from production import read,write,sha,now
import finalize_scoped as f
ctx=f.context('r11_c13','1aa087f96cf986582881560436fb3fba780cbcbe13f3b29a133e4eb9c0ece180');required=f.requirements(ctx)
def item(path,observation):
 p=Path(path);rec=copy.deepcopy(read(str(p)+'.generation.json'));im=Image.open(p).convert('RGB');key=f.key(p)
 expected=required[key]['image'] if key in required else f.extra_image(ctx,p,rec)
 assert sha(p)==rec['sha256'] and np.array_equal(np.asarray(im),np.asarray(expected))
 rec.update(actuallyViewed=True,reviewer='root',viewTool='view_image detail original',newVisualInspectionClaimed=True,exactCurrentPixelsReproduced=True,pixelSha256=hashlib.sha256(im.tobytes()).hexdigest(),nativeScale=1,verdict='current_pixels_inspected_neighbor_unverified' if 'no-neighbor-unverified' in p.name else 'scoped_pass',observations=observation)
 return rec
observations={
'internal-x1024-full':'Blue canopy edge and seam, warm timber joints, cargo crate and stone masonry contours continue through all four sections without a rectangular paint step.',
'internal-x1024-return-256-full':'Canopy white stripe, frame highlights, crate masonry and quay wall return to native paint continuously.',
'internal-x2048-full':'Stall timber, warm paving, crate edge and water post are continuous across all four seam centers.',
'internal-x2048-return-256-full':'Timber grain, paving grout and quay masonry have no visible finite-return boundary.',
'internal-x3072-full':'Water fender, angled curb, paving and lower waterline show continuous contour and brushwork.',
'internal-x3072-return-256-full':'Cobalt water shapes, paving illumination and masonry edges remain coherent across the finite return.',
'west-return-256-full':'Left stall platform, warm paving, wooden crate and quay coping show continuous paint through the return.',
'north-shared-full':'Actual north canopy cloth/stripe, timber rail/post and masonry/water endpoints connect to the current native tile.',
'north-return-256-full':'Canopy, stall wood and cobalt-to-gold water reflections transition without a horizontal tone band.',
'west-no-neighbor-unverified':'Current west platform and paving edge inspected; no actual west neighbor exists, so cross-tile seam remains unverified.',
'east-no-neighbor-unverified':'Current water and clipped boat edge inspected; east neighbor absent, seam unverified.',
'south-no-neighbor-unverified':'Current masonry, timber fenders and water inspected; south neighbor absent, seam unverified.'}
root_items=[];ext_items=[]
for label,obs in observations.items():
 p=F/'qa'/('west-no-neighbor-unverified.png' if label=='west-no-neighbor-unverified' else 'native-candidate/'+label+'.png')
 (ext_items if label in ['north-shared-full','north-return-256-full'] else root_items).append(item(p,obs))
for i,obs in enumerate(['The left canopy diagonal edge, blue fabric panels and post are continuous at the true join.','The pale cloth stripe and canopy hem remain a single aligned form across the join.','Wooden upright/rail, masonry and round water post connect with coherent thickness and lighting.','Broad cobalt water cells and golden reflections connect naturally; no straight warm/cool band at the true N edge.'],1):
 ext_items.append(item(F/f'qa/external-details/north-segment-{i}.png',obs))
assert len(root_items)==10 and len(ext_items)==6
for name,items,flag in [('root-review.json',root_items,'scopedPass'),('external-review.json',ext_items,'externalScopedPass')]:
 p=F/'qa'/name;assert not p.exists();write(p,dict(reviewedAt=now(),reviewer='root',candidate=f.ref(ctx['candidate']),items=items,count=len(items),issueCount=0,issues=[],**{flag:True},formalAccepted=False,navigationVerified=False,clientVerified=False,scope='Actual visual review of current pixels. Absent west/east/south neighbors remain unverified.'))
print('Recorded10 root and6 external actual original-pixel reviews; all pixels reproduced; no candidate changes.')

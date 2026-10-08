from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
f=ROOT/'r09_c14';q=f/'qa/north-no-neighbor-unverified.png'
r=read(f/'qa/root-review.json')
assert not any(i['file']==str(q) for i in r['items'])
r['items'].append(dict(file=str(q),sha256=sha(q),actuallyViewed=True,nativeScale=1,viewTool='view_image',viewDetail='original',verdict='current_pixels_inspected_neighbor_unverified',review='All4096 native north boundary pixels viewed. Cropped lamp, flowers, tree, foliage and rock retain clear continuous painting. North neighbor missing; no shared-edge acceptance.'))
r['wholeTilePreviewActuallyViewed']=True
r['wholeTilePreviewScale']='4096 image displayed at1600; composition/style review only, not seam acceptance'
r['compositionReview']='Rounded clean Daoist night market framing preserved. Crisp native foreground crate repair matches the planned footprint.'
write(f/'qa/root-review.json',r)
write(f/'progress.json',dict(updatedAt=now(),tile='r09_c14',nativePatches=16,pixels=[4096,4096],completePixelCoverage=True,candidate=r['candidate'],scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,stage='west_foliage_AI_repair',missingExternalNeighbors=['north','east','south']))
print('Actual root north and composition reviews recorded; west issue still pending.')

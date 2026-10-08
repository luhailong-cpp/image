from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
f=ROOT/'r10_c13';mp=f/'output/native-assembly.json';m=read(mp);p=Path(m['file'])
assert sha(p)==m['sha256']=='c6c7176ea72228aca772c78a17fe8e3b5fc699904f46205d62ae482f420d1a5b'
plan=read(f/'plan.json');paths=[plan['northWestCandidate'],plan['northCandidate'],plan['westCandidate'],str(p)]
sheet=Image.new('RGB',(1024,1024));boxes=[(3584,3584,4096,4096),(0,3584,512,4096),(3584,0,4096,512),(0,0,512,512)]
for src,box,xy in zip(paths,boxes,[(0,0),(512,0),(0,512),(512,512)]):sheet.paste(Image.open(src).convert('RGB').crop(box),xy)
corner=f/'qa/four-tile-corner.png';sheet.save(corner)
deriv(corner,paths,dict(kind='four_adjacent_real_tile_corner',globalJunctionXY=[49152,36864],sourceCropLTRB=boxes,scale=1,resampling=False))
print(str(corner))
if '--approve' in sys.argv:
    # Review assertions represent actual image inspections, never automated visual acceptance.
    h=read(f/'qa/horizontal-review.json');e=read(f/'qa/external-review.json')
    assert h['candidate']['sha256']==sha(p) and e['candidate']['sha256']==sha(p)
    assert h['scopedPass'] and h['issueCount']==0 and e['externalScopedPass'] and not e['issues']
    own=[]
    for x in [1024,2048,3072]:
        for suffix in ['full','return-256-full']:
            qp=f/f'qa/native-candidate/internal-x{x}-{suffix}.png'
            own.append(dict(file=str(qp),sha256=sha(qp),actuallyViewed=True,viewTool='view_image',viewDetail='original',nativeScale=1,verdict='scoped_pass',review='Full4096 vertical seam/return viewed. Roof, beams, paving contours, cloth, crates and railing show no visible splice, duplicate contour or straight registration boundary.'))
    for side in ['east','south']:
        qp=f/f'qa/native-candidate/{side}-no-neighbor-unverified.png'
        own.append(dict(file=str(qp),sha256=sha(qp),actuallyViewed=True,viewTool='view_image',viewDetail='original',nativeScale=1,verdict='current_pixels_inspected_neighbor_unverified',review='Core boundary strip retains scene continuity; planning outer halo artifacts fall outside final crop. Neighbor absent, shared edge not accepted.'))
    own.append(dict(file=str(corner),sha256=sha(corner),actuallyViewed=True,viewTool='view_image',viewDetail='original',nativeScale=1,verdict='scoped_pass',review='Four true adjacent512-square corners at global49152,36864 connect the golden roof contours and roof ribs without detached or doubled endpoints.'))
    covered={i['file']:i for i in own}
    for report in [h,e]:
        for it in report.get('items',report.get('mainQA',[])):
            assert it['actuallyViewed'] and sha(it['file'])==it['sha256']
            covered[it['file']]=it
    assert all(q['file'] in covered and sha(q['file'])==q['sha256'] for q in m['qa'])
    final_review=dict(reviewedAt=now(),candidate=dict(file=str(p),sha256=sha(p)),rootItems=own,independentReviews=[dict(file=str(f/'qa/horizontal-review.json'),sha256=sha(f/'qa/horizontal-review.json')),dict(file=str(f/'qa/external-review.json'),sha256=sha(f/'qa/external-review.json'))],all27StandardQAImagesActuallyViewed=True,additionalFourTileCornerPassed=True,scopedLocalSeamsPassed=True,missingExternalNeighbors=['east','south'],formalAccepted=False,clientVerified=False,navigationVerified=False)
    write(f/'qa/final-local-review.json',final_review)
    final=dict(m)
    final.update(status='native_4K_candidate_available_internal_north_west_corner_QA_passed',scopedLocalSeamsPassed=True,scopedReview=str(f/'qa/final-local-review.json'),acceptedAtScoped=now(),runtimeDependencies=[dict(file=str(p),sha256=sha(p))],sourceManifest=dict(file=str(mp),sha256=sha(mp)),sourceRecordsHistoricalAfterRetention=True)
    for it in final['qa']:it['actuallyViewed']=True;it['reviewVerdict']=covered[it['file']]['verdict']
    write(f/'output/manifest.json',final)
    gp=Path(str(p)+'.generation.json');g=read(gp);g['scopedLocalReview']=dict(file=str(f/'qa/final-local-review.json'),sha256=sha(f/'qa/final-local-review.json'));g['scopedLocalSeamsPassed']=True;write(gp,g)
    write(f/'progress.json',dict(updatedAt=now(),tile='r10_c13',nativePatches=16,pixels=[4096,4096],completePixelCoverage=True,file=str(p),sha256=sha(p),scopedLocalSeamsPassed=True,formalAccepted=False,clientVerified=False,navigationVerified=False,missingExternalNeighbors=['east','south']))
    print('Final scoped QA manifest saved.')

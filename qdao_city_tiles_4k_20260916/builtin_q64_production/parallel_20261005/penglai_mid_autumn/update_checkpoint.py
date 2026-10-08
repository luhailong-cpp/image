from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from production import ROOT, read, write, sha, now

evidence = read(ROOT/'tools/multi_edge/test-evidence.json')
for tool in evidence['tools']:
    assert sha(tool['file']) == tool['sha256']
assert evidence['result'] == 'pass'
write(ROOT/'tools/multi_edge/root-code-review.json',dict(reviewedAt=now(),reviewer='/root',filesActuallyRead=evidence['tools'],testEvidence={'file':str(ROOT/'tools/multi_edge/test-evidence.json'),'sha256':sha(ROOT/'tools/multi_edge/test-evidence.json')},result='pass_for_first_NE_pilot',issues=[],inspection=['Physical patch coordinates and input images remain unreflected; numeric registration reflects and restores vector signs.','North/east/south/west and true diagonal context crops preserve global coordinates; bounded finite registration retains existing support.','Prepare/save reject in-flight or modified inputs; explicit stable plan opt-in is required.','QA covers all perimeter pixels, reverse finite return lines and true four-tile corners.'],productionUseAllowed='First NE pilot r10_c11 only, after structure review; each actual seam still requires visual QA.',bulkProductionAccepted=False,formalAccepted=False))
p=read(ROOT/'progress.json');p.update(currentTile='r10_c14',parallelNextTile='r10_c11',currentCandidate=str(ROOT/'r09_c14/output/r09_c14-candidate.png'));write(ROOT/'progress.json',p)
c=read(ROOT/'continuation-20261008.json')
c.update(updatedAt=now(),completePixelCandidates=7,missingTiles=249,formallyAcceptedTiles=0)
c['r09_c14']=dict(candidate='r09_c14/output/r09_c14-candidate.png',sha256=sha(ROOT/'r09_c14/output/r09_c14-candidate.png'),nativePatches=16,scopedAcceptance='Internal seams and actual west neighbor passed; N/E/S absent remain unverified.',review='r09_c14/qa/final-local-review.json',manifest='r09_c14/output/manifest.json',repair='r09_c14/repairs/west-foliage/application-v9.json',formalAccepted=False)
c['r10_c14'].update(nativePatches=len(list((ROOT/'r10_c14/native').glob('p[1-4][1-4].png'))),firstRow='p11..p14 saved; p11 surface AI repaired before downstream generation.',upperTwoRowsGuidesFrozen=True,row2Agent='/root/r09c14_row3_resume',row3Agent='/root/r09c14_row2_resume',row4Agent='/root/r09c14_row4_resume',parallelRequest='Upper two rows safe to proceed; lower beam thickness refinement and guide review still pending. North source SHA migration delegated to structure agent.')
c['fullMapTraversal'].update(isolatedImplementationInProgress=False,implementation='tools/multi_edge',rootReview='tools/multi_edge/root-code-review.json',productionStatus='Code/test review passed for first NE pilot after structural review. No bulk acceptance.')
write(ROOT/'continuation-20261008.json',c)
print('Checkpoint and multi-edge pilot code review recorded.')

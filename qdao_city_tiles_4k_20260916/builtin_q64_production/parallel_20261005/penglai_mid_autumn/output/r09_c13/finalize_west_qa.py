"""Record completed native visual QA. Does not modify any production pixels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from PIL import Image

B = Path(__file__).resolve().parents[2]
O = B / 'output/r09_c13'
Q = B / 'qa/west-final'
H = B / 'repairs/west/closure3'
NOW = datetime.now(timezone.utc).isoformat()
EXPECTED = '9de5b3325de9ba147072aab2b5e7effbbd10a033894b928711e572b895429e4d'
OLD_HASH = '59b31c2d193a71fdfe516ad9d51c6d2bfea3881f5670dd9f53ba2a612ad59fd2'
BASE_HASH = '2f4c1e8f489d8c20332d0107a1889287da36e30a21d921f16e7d508dec44edb0'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, d): Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def ref(p): return {'file': str(p), 'sha256': sha(p)}

m = read(O / 'manifest.json')
g = read(O / 'r09_c13.png.generation.json')
r = read(Q / 'review.json')
t = read(H / 'merge-trial-record.json')
assert sha(O / 'r09_c13.png') == EXPECTED == m['sha256'] == g['sha256'] == r['source']['sha256']
assert sha(m['westSource']) == OLD_HASH
base = B / 'assembly-registered/r09_c13-candidate.png'
assert sha(base) == BASE_HASH
pixels = np.asarray(Image.open(O / 'r09_c13.png'))
assert pixels.shape == (4096, 4096, 3)
assert np.array_equal(pixels[:, 500:], np.asarray(Image.open(base))[:, 500:])

findings = {
 'shared-full.png': 'Full 4096px west edge continuous. Natural post shadows and roof highlights preserved; no unmatched paving stub or vertical independent color seam.',
 'return-x100-full.png': 'Full x100 return continuous, including approved roof endpoint registration return.',
 'return-x256-full.png': 'Full x256 color-field return continuous; no horizontal bands, artwork blur or new outline shift.',
 'return-x500-full.png': 'Full x500 west-band return continuous; paving seams and highlights align.',
 'repair-crossing-1100.png': 'Repair crossing y1100: same-material paving tone and contour continuous.',
 'repair-crossing-2050.png': 'Repair crossing y2050: paving and nearby diagonal joint continuous.',
 'repair-crossing-3000.png': 'Repair crossing y3000: rail/post and paving edges continuous.',
 'internal-crossing-1024.png': 'Internal horizontal seam y1024 through west band and its return continuous.',
 'internal-crossing-2048.png': 'Internal horizontal seam y2048 through west band and its return continuous.',
 'internal-crossing-3072.png': 'Internal horizontal seam y3072 through west band and its return continuous.',
 'endpoints.png': 'North wood/step and south roof endpoint contours and highlights continue across the west shared edge.',
 'endpoint-return-region.png': 'Approved roof registration flows continuously into unchanged native pixels at x100; no added roof structure.',
 'shared-unrotated-1.png': 'y0..1024: wood post shadow and blue step top/side boundaries are natural object contours, not missing geometry.',
 'shared-unrotated-2.png': 'y1024..2048: paving illumination and joints continuous, including bounded color correction return.',
 'shared-unrotated-3.png': 'y2048..3072: formerly 72px-disconnected grout and orphan grout stub resolved; intended diagonal joint and pillar retained.',
 'shared-unrotated-4.png': 'y3072..4096: rail and roof contours continuous; original material facets and approved endpoint correction retained.',
}
assert len(r['qa']) == len(findings) == 16
for q in r['qa']:
    name = Path(q['file']).name
    assert sha(q['file']) == q['sha256'] and name in findings
    q.update(actuallyViewed=True, reviewedAt=NOW, viewTool='view_image detail=original', viewScale=1,
             reviewer='/root/audit_structure', verdict='pass_in_scope', finding=findings[name])

assert len(r['finalMicroQA']) == 16
for i, q in enumerate(r['finalMicroQA']):
    assert sha(q['file']) == q['sha256']
    finding = 'No broken contour, unmatched endpoint or unnatural vertical color seam in this native 256px interval.'
    if i in (8, 9): finding = 'Original 72px-disconnected paving joint is now continuous; highlights and dark grout connect.'
    if i in (10, 11): finding = 'Orphan rising grout stub removed. Intended descending joint and rail/post contour retained and continuous.'
    q.update(actuallyViewed=True, reviewedAt=NOW, viewTool='view_image detail=original', viewScale=1,
             reviewer='/root/audit_structure/north_edge_audit', verdict='pass_in_scope', finding=finding)

for q in t['qa']:
    assert sha(q['file']) == q['sha256']
    q.update(actuallyViewed=True, reviewedAt=NOW, reviewer='/root/audit_structure',
             viewTool='view_image detail=original', verdict='pass_in_scope')
t['visualReviewPending'] = False
t['visualReview']['finalProductionQaResult'] = 'scoped_local_seams_passed'
t['visualReview']['finalProductionSha256'] = EXPECTED
write(H / 'merge-trial-record.json', t)
operation = m['structuralClosure']
operation['repairEvidence'] = ref(H / 'merge-trial-record.json')

resolved = list(r.get('resolvedDefects', []))
resolved.extend([
 {'id': 'W-NORTH-CONTOUR-01', 'status': 'natural_contour_confirmed_no_additional_modification',
  'newTileYRange': [50, 300], 'finding': 'Actual original-pixel inspection and independent audit confirm old support lies on natural post shadow/rail contour. Protected geometry remains unchanged.'},
 {'id': 'W-GROUT-01', 'status': 'resolved_by_native_AI_reconstruction', 'newTileYRange': [2205, 2320],
  'finding': 'The old-left joint at y2304 and prior new-right joint around y2232 were different structures, beyond finite registration. Native AI source now supplies the missing continuous connection.'},
 {'id': 'W-GROUT-02', 'status': 'resolved_by_native_AI_reconstruction', 'newTileYRange': [2740, 2785],
  'finding': 'Unsupported ascending grout stub removed by AI repaint. Existing descending joint at y2846..2848 and post retained.'},
 {'id': 'W-RESIDUAL-COLOR-03', 'status': 'triaged_and_closed_by_native_inspection', 'newTileYRange': [1696, 2934],
  'finding': 'Original broad concern contained two genuine structural errors handled above. Final same-material surfaces are continuous; independent 16-window audit found no residual unnatural vertical color seam. No broad color field was used to conceal geometry.'},
])
resolved = list({d['id']: d for d in resolved}.values())
baseline_evidence = {
 'file': str(base), 'sha256': BASE_HASH, 'priorInternalQa': m['internalQA'],
 'finalFile': str(O / 'r09_c13.png'), 'finalSha256': EXPECTED,
 'pixelEqualityVerifiedRectXYWH': [500, 0, 3596, 4096], 'changedPixelsInRect': 0,
 'updatedWestCrossingsActuallyViewed': [1024, 2048, 3072],
 'conclusion': 'Prior full internal seam QA remains valid outside west x0..500; final native crops cover each affected horizontal crossing and return.'
}
r.update(reviewedAt=NOW, result='scoped_local_seams_passed', scopedLocalSeamsPassed=True,
         internalAndWestScopedPassed=True, formalAccepted=False, clientVerified=False,
         navVerified=False, navigationVerified=False, wholeTileAccepted=False,
         sourceHashReverified=True, oldWesternSourceHashReverified=True,
         defects=[], remainingPureColorVsStructureUncertainty=[], resolvedDefects=resolved,
         returnEdgesPassed=True, repairCrossingGeometryPassed=True, internalCrossingGeometryPassed=True,
         endpointCorrectionGeometryPassed=True, internalBaselineContinuity=baseline_evidence,
         structuralClosure=operation, missingExternalNeighborQA=['north','east','south'],
         recommendedNextStep='Only future north/east/south neighbor QA and client/navigation checks remain outside this scope.',
         reviewBasis='Sixteen full/native context QA images actually viewed by audit_structure plus all sixteen consecutive 320x256 west micro-windows independently viewed by north_edge_audit. Twelve native merge-return crops verified before merge. Pixel equality after x500 preserves prior internal QA. This supersedes earlier broad-image classifications.',
         scope='Internal tile seams plus the entire west shared edge y0..4096, west repair crossings, native repair mask returns and x100/x256/x500 returns; excludes missing north/east/south neighbors, formal acceptance, client and navigation.')
write(Q / 'review.json', r)
qa_ref = ref(Q / 'review.json')
m.update(updatedAt=NOW, status='scoped_local_seams_passed', scopedLocalSeamsPassed=True,
         internalAndWestScopedPassed=True, formalAccepted=False, clientVerified=False,
         navigationVerified=False, navVerified=False, wholeTileAccepted=False,
         remainingScopedDefects=[], resolvedScopedDefects=resolved, westFinalQA=qa_ref,
         qa=r['qa'], finalMicroQA=r['finalMicroQA'], internalBaselineContinuity=baseline_evidence,
         missingExternalNeighborQA=['north','east','south'])
m['internalQA']['westSharedEdge'] = 'passed final native scoped QA; see westFinalQA'
g.update(updatedAt=NOW, status='scoped_local_seams_passed', scopedLocalSeamsPassed=True,
         internalAndWestScopedPassed=True, formalAccepted=False, clientVerified=False,
         navigationVerified=False, navVerified=False, wholeTileAccepted=False,
         qa=qa_ref, operation=operation)
write(O / 'manifest.json', m)
write(O / 'r09_c13.png.generation.json', g)

for i, label in [(2, 'upper'), (3, 'lower')]:
    p = H / f'attempt{i}.png.generation.json'
    d = read(p)
    d.update(status='partially_used_native_source', finalizedAt=NOW, sourceRetained=True,
             appliedMask=ref(H / f'{label}.mask.png'), productionOutput=ref(O / 'r09_c13.png'),
             usage='Only the named registered binary-mask region is applied; other pixels are not accepted production artwork.')
    write(p, d)

# The rejected project copy is not an active source. Keep provenance text, no rejected image backup.
rejected = H / 'attempt1.png'
side = H / 'attempt1.png.generation.json'
d = read(side)
if rejected.exists():
    assert rejected.resolve().parent == H.resolve() and sha(rejected) == d['sha256']
    rejected.unlink()
d.update(projectCopyRetained=False, projectCopyRemovedAt=NOW,
         retainedTextEvidence=True, removalReason='Rejected old-left geometry changed; no pixels used in production. Active sources are attempt2 and attempt3.')
write(side, d)

assert sha(O / 'r09_c13.png') == EXPECTED and sha(m['westSource']) == OLD_HASH
print(json.dumps({'status':m['status'], 'file':m['file'], 'sha256':EXPECTED, 'qa':qa_ref,
                  'mainNativeQaCount':len(r['qa']), 'independentMicroQaCount':len(r['finalMicroQA']),
                  'mergeNativeQaCount':len(t['qa']), 'outsideWestBandPixelsUnchanged':True,
                  'formalAccepted':False,'clientVerified':False,'navVerified':False},ensure_ascii=False))

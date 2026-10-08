"""Persist actual native-pixel visual review of the current c13/c14 joint."""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
QA = ROOT / 'r08_c14/repairs/west-common-edge/integration-qa'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest = json.loads((QA / 'manifest.json').read_text(encoding='utf-8'))
for item in manifest['outputs'] + manifest['qa']:
    assert sha(item['file']) == item['sha256'], item['file']
assert len(manifest['qa']) == 10
review = {
    'reviewedAtUtc': datetime.now(timezone.utc).isoformat(),
    'reviewer': 'close_joint14',
    'method': 'Actual view_image original-detail inspection of all ten native-pixel QA images; images are rearranged/cropped without resampling.',
    'outputs': manifest['outputs'],
    'reviewedImages': [dict(item, visualInspection='pass-no-actionable-joint-defect-observed') for item in manifest['qa']],
    'coverage': dict(manifest['coverage'], visualReview='complete'),
    'findings': [],
    'observations': [
        'Full 4096-pixel common edge: blue water shapes, warm stone joints, shadows, and central timber post connect continuously.',
        'Both full insertion bands: rope/post silhouettes, basket contours, timber/crate edges, water and paving have no observed cut, doubled contour, or abrupt insertion step.',
        'All three horizontal overlaps and all four insertion corners: no actionable discontinuity observed at native pixel scale.'
    ],
    'pixelValidation': {
        'integrationManifest': str(ROOT / 'tiles/west-integration-r08_c14-manifest.json'),
        'integrationManifestSha256': sha(ROOT / 'tiles/west-integration-r08_c14-manifest.json'),
        'c13WestRepairsPreserved': True,
        'c14WaterRepairedImmutableOutputPreserved': True,
        'outsidePairRectXYXYExactlyPreserved': [3469, 0, 4723, 4096]
    },
    'formalAccepted': False,
    'wholeCityComplete': False,
    'scope': 'c13/c14 shared-edge and repair insertion QA only; client/navigation acceptance is not implied.'
}
(QA / 'review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'review': str(QA / 'review.json'), 'outputs': manifest['outputs'], 'findings': 0}))

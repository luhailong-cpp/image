"""Record human/model visual observations after viewing derived references."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
REPO = Path('D:/work/image')
NOW = datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def write(p, d):
    p = Path(p)
    assert p.resolve().is_relative_to(OUT)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


prep = read(OUT / 'preparation.json')
refs = [
    (OUT / 'guides/shared-layout-with-west-context-1254.png', 'Image1: actual mapped shared layout plus west neighbor context; layout only'),
    (OUT / 'guides/west-r09_c10-exact230x4326.png', 'Image2: exact unresampled west native strip; full height; native boundary source'),
    (REPO / 'designs/gameplay-ui/04-guild.png', 'Image3: user-confirmed PRIMARY painting and material style only'),
]
records = [{'file': p.as_posix(), 'sha256': sha(p), 'role': role, 'actuallyViewedBeforePrompt': True} for p, role in refs]
for rec in prep['sources']:
    assert sha(rec['file']) == rec['sha256'], f"Source changed since preparation: {rec['file']}"
for rec in prep['artifacts']:
    assert sha(rec['file']) == rec['sha256']
review = {
    'schemaVersion': 1, 'reviewedAtUtc': NOW, 'tile': 'r09_c11',
    'status': 'guide_visual_inspection_completed_not_art_or_seam_acceptance',
    'viewedReferences': records,
    'observedFeatures': [
        {'feature': 'Existing arched pale-stone bridge', 'scope': 'Main diagonal structure from west boundary across the center toward lower-right steps. Preserve arch opening, piers and bridge width; no new bridge.'},
        {'feature': 'Gray-white stone balustrades and capped square posts', 'scope': 'Both sides of bridge. Exact west band determines the entering post, near-side rail and arch contours; the soft macroguide is not pixel truth.'},
        {'feature': 'Cream deck, steps and landing', 'scope': 'Open central bridge deck descends by existing steps toward lower right. Preserve traversable route and step orientation.'},
        {'feature': 'Turquoise-blue river', 'scope': 'Upper-right water and lower-left water under the arch; keep water extent and bank topology.'},
        {'feature': 'Existing trees and shrubs', 'scope': 'Clipped trees/canopies/trunks at top and right; lower-edge clipped green shrubs. Preserve these existing occupied envelopes, do not create extra planting.'},
    ],
    'historicalNavigationReferences': ['east lower stone bridge', 'lower east bridge surface'],
    'navigationNameUse': 'Historical identifiers only, not public game place names or proof of current-art alignment.',
    'boundaryObservations': [
        'The guide has an expected mixed-resolution vertical paste boundary at extended x230. It must not be painted as a physical structure.',
        'Native west source geometry and low-resolution day guide are not proven to match in exact local positions. Continue the native endpoints while preserving mapped bridge/shore topology; review before16-piece production.',
        'The full-height west strip was refreshed from tone-refined selected-v2 and viewed at original230x4326 pixels. Water now has smoother tonal flow, without the broad rectangular water-tone break of the older source. A narrow horizontal tonal/edge transition remains across part of the lower clipped foliage around extended y3187; do not claim that every source irregularity was removed. No source image was edited here. This guide-only inspection does not accept the future east-west seam.',
    ],
    'sourceQualifiedForBoundaryPlanning': True,
    'geometryAlignmentAccepted': False, 'externalWestSeamAccepted': False,
    'newArtworkNavigationAccepted': False, 'formalAccepted': False,
    'crossAppearancePairVerificationPending': True,
    'noAIGenerationPerformed': True,
}
write(OUT / 'guide-visual-review.json', review)
request = {
    'schemaVersion': 1, 'preparedAtUtc': NOW, 'status': 'prepared_not_submitted',
    'tile': 'r09_c11', 'purpose': 'single neutral day/spring shared structural region guide',
    'promptFile': (OUT / 'regional-prompt-pending.txt').as_posix(),
    'promptSha256': sha(OUT / 'regional-prompt-pending.txt'), 'references': records,
    'generationAllowedInThisPreparationStep': False, 'toolCalled': False,
    'submittedParameters': {'model': None, 'quality': None}, 'actualModel': None, 'actualQuality': None,
    'configSnapshot': read(OUT / 'source-evidence/config-snapshot.json'),
    'qualityVerificationScope': 'No model call made. Root must follow current batch official verification and preserve actual tool evidence when submitting.',
    'formalAccepted': False, 'crossAppearancePairVerificationPending': True,
    'needsBeforeNativeProduction': 'Inspect generated shared region against exact west strip and mapped guide. Resolve the bridge/railing continuation without claiming a second independent day layout. New native boundary artwork and its eventual seam require independent QA.',
}
write(OUT / 'regional-request-pending.json', request)
prep['visualInspection'] = {'file': (OUT / 'guide-visual-review.json').as_posix(), 'sha256': sha(OUT / 'guide-visual-review.json')}
prep['pendingRegionalRequest'] = {'file': (OUT / 'regional-request-pending.json').as_posix(), 'sha256': sha(OUT / 'regional-request-pending.json')}
prep['lastSourceRecheckUtc'] = NOW
write(OUT / 'preparation.json', prep)
print(json.dumps({'status': request['status'], 'references': records, 'writeScope': OUT.as_posix(), 'newGeneratedImages': 0}, ensure_ascii=False))

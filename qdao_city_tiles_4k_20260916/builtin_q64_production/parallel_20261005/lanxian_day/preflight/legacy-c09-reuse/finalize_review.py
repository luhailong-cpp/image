from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
record=json.loads((OUT/'diagnostic.json').read_text(encoding='utf-8'))
for source in record['sources'].values():
    assert sha(source['file'])==source['sha256']
for view in record['images']:
    assert sha(view['file'])==view['sha256']
handoff_path=Path(record['handoffAtDiagnostic']['file'])
handoff=json.loads(handoff_path.read_text(encoding='utf-8-sig'))
review={
    'createdAtUtc':datetime.now(timezone.utc).isoformat(),
    'status':'reusable_initial_native_candidate_against_recorded_legacy_west_neighbor',
    'formalAccepted':False,
    'wholeTileAccepted':False,
    'runtimePublished':False,
    'diagnostic':{'file':str(OUT/'diagnostic.json'),'sha256':sha(OUT/'diagnostic.json')},
    'sources':record['sources'],
    'actuallyViewed':[
        {'file':str(OUT/'common-edge-all1139.png'),'sha256':sha(OUT/'common-edge-all1139.png'),'method':'view_image detail original; unscaled native strip'},
        {'file':str(OUT/'same-world-overlap-side-by-side.png'),'sha256':sha(OUT/'same-world-overlap-side-by-side.png'),'method':'view_image detail original; same-world overlap alternatives, no blending'},
        {'file':record['sources']['legacyPatch']['file'],'sha256':record['sources']['legacyPatch']['sha256'],'method':'view_image detail original; complete1254x1254 native source'}
    ],
    'geometryScope':{
        'c09LocalYHalfOpen':[0,1139],
        'coreCoverageC09LocalXYXY':[0,0,1024,1024],
        'westCommonBoundaryGlobalX':32768,
        'commonBoundaryGlobalYHalfOpen':[28672,29811],
        'sameWorldOverlapSourceBoxes':{'c08':[3981,0,4096,1139],'c09Native':[0,115,115,1254]}
    },
    'observations':[
        'Viewed the full 1139-pixel west common edge at native resolution. The gray inset outline, dark recessed ring, gray ring and ivory beveled surround cross the seam without an obvious broken contour, duplicate ring or large position jump.',
        'Gray stone and warm ivory ground retain compatible hand-painted material and lighting. Small brushwork differences remain across the seam and the same-world overlap is not pixel-identical; no broad dark or bright vertical band was visible in the inspected strip.',
        'The full native patch has a coherent circular boundary and radial slab joints. No obvious malformed joint or blurred edge was seen that would justify discarding and regenerating this initial source.',
        'The native source is suitable as an initial candidate for reuse, conditional on verifying it against the final handoff c08 or proving the inspected east-edge source pixels are unchanged.',
        'This review does not cover the ungenerated c09 interior patches, the patch north/east/south neighbor joins, the full4096-pixel tile edge, cross-appearance alignment, navigation, or client rendering.'
    ],
    'recommendedAction':'Retain and cite this native source. Reuse as local patch r01_c01 if the final handoff c08 inspected boundary is unchanged; otherwise rerun this limited boundary comparison before deciding whether a localized repair is needed. Do not count a completed4K tile.',
    'handoffAtReview':{'file':str(handoff_path),'sha256':sha(handoff_path),'readyForProduction':handoff['readyForProduction'],'thisReviewDoesNotPromoteHandoff':True},
    'numericDiagnostics':record['sameWorldOverlapDiagnostics'],
    'unchangedLegacySources':True
}
(OUT/'visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'review':str(OUT/'visual-review.json'),'status':review['status'],'formalAccepted':False},ensure_ascii=False))

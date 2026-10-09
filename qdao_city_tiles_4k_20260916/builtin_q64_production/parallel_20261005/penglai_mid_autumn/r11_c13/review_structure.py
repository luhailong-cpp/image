from prepare_structure import *
plan=read(F/'plan.json');src=Path(plan['nightStructure']);index=read(F/'guides/index.json')
assert sha(N)==NSHA and sha(DAY)==DAY_SHA
assert len(index['records'])==16 and not list((F/'native').glob('*.png'))
for row in index['records']:
    assert sha(row['file'])==row['sha256'];assert Image.open(row['file']).size==(1254,1254)
files=[src,Q/'core-preview.png',Q/'north-target-context.png']+[Q/f'north-join-segment{i}.png' for i in range(1,5)]
notes=[
 'Full planning composition actually viewed. Bright rounded blue-violet/amber night style, coherent cargo/quay/water/cropped boat and no sky. Current full frame4736 retained. Local selection joins remain planning paint, not native production acceptance.',
 'Core view actually viewed. Existing occupied footprints, dock wall and cropped boat remain readable; canopy native-edge correction changes local fold placement only. No extra stall, roof or cargo added.',
 'N above target context actually viewed. Large native canopy continues into target without the earlier side-jump; quay and existing timber structure connect macroscopically. Fine paint/light differences at boundary require native generation and later real seam QA.',
 'Segment1 actually viewed at original1024x640: canopy edge and pale stripe flow across boundary; no large doubled canopy step. Minor shade/brushwork needs native matching.',
 'Segment2 actually viewed at original1024x640: prior approximately70-100global-pixel pale stripe jump removed by focused AI repair; one hem and stripe continue. Narrow color/paint boundary remains planning-only and must be repainted from actual N.',
 'Segment3 actually viewed at original1024x640: wooden upright, diagonal beam and quay wall remain connected with their intended count and thickness. Small endpoint/edge paint differences must follow actual native context, no new attachment.',
 'Segment4 actually viewed at original1024x640: wall waterline and fender occupy correct continuation; target water adds warm reflections, so native p14 must transition ripple/color without a horizontal band. No physical geometry shift observed.'
]
views=[ref(p,actuallyViewed=True,detail='original',reviewer='/root/r09c14_row4_resume',note=note) for p,note in zip(files,notes)]
report=dict(reviewedAt=now(),reviewer='/root/r09c14_row4_resume',notRootReview=True,status='macro_structure_proposal_ready_for_root_review',rootReviewPending=True,nativeGenerationAuthorized=False,nativePatchCount=0,formalAccepted=False,nativeSeamAccepted=False,navigationVerified=False,clientVerified=False,north=ref(N),daySource=ref(DAY),dayTaskModified=False,currentStructure=ref(src),referenceFrameGlobalXYWH=FRAME,planningExtended4326=ref(plan['planningExtended4326']),guideIndex=ref(F/'guides/index.json'),actualViews=views,checks=dict(guideCount=16,allGuidePixels=[1254,1254],all24AdjacentOverlapsPixelIdentical=True,allGuidesPlanningOnly=True,currentNorthUnchanged=True,readOnlyDaySourceUnchanged=True),remainingNativeRequirements=plan['nativePatchConstraints'],generationLimitations='Configured gpt-image-2.5-sunburst/max are target values only. Builtin route exposes no model or quality selector and actual values remain null in each AI record.',missingNeighborScopes=['west','east','south','northwest'])
write(Q/'structure-review.json',report)
write(F/'guides/frozen-for-root-review.json',dict(createdAt=now(),stage='proposal freeze awaiting root review; not native authorization',structure=ref(src),plan=ref(F/'plan.json'),source=ref(plan['planningExtended4326']),guideIndex=ref(F/'guides/index.json'),guides=[ref(r['file'],id=r['id']) for r in index['records']],north=ref(N),nativePatchCount=0))
print(json.dumps(dict(structure=ref(src),guideIndex=ref(F/'guides/index.json'),review=ref(Q/'structure-review.json')),indent=2))

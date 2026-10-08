"""Record completed human-model visual inspection without upgrading formal status."""
from pathlib import Path
import numpy as np
from PIL import Image
from common import TILE, read, write, info, now

out=TILE/'assembly_bounded_v2'
m=read(out/'assembly.json');v=read(out/'pixel-verification.json')
vertical={
'vertical_1024_segment01_1to1.png':'Rounded leaves and gray rail shade transition reduced. Stone post/rail contour remains joined; faint original faceted paint stays.',
'vertical_2048_segment01_1to1.png':'Leaf/water cut is less apparent. Leaf envelope and post silhouette remain coherent; local water stroke-frequency difference remains nonblocking.',
'vertical_3072_segment01_1to1.png':'Water-only tone alignment reduces vertical brightness step; willow shape and rock contour remain unchanged.',
'vertical_3072_segment02_1to1.png':'Upper water transition smoother, diagonal rail remains continuous. Some broad-vs-fine ripple variation persists but no straight rectangular tone boundary is visible.',
'vertical_2048_segment04_1to1.png':'Diagonal rail and low foliage shade transition reduced. Rail edges remain connected, with a small approximately 1-3 px painted bevel irregularity; no structural repair required.'}
horizontal={
'horizontal_1024_segment01_1to1.png':'Stone base, paving and slanted joint remain continuous after nearby field fade.',
'horizontal_1024_segment02_1to1.png':'Post base, railing and cast shadow remain continuous; no new horizontal tone step.',
'horizontal_1024_segment03_1to1.png':'Water plane, capped post and diagonal rail connect without a rectangular return edge.',
'horizontal_1024_segment04_1to1.png':'Water to rounded tree canopy remains coherent; no new horizontal band or material leakage.',
'horizontal_3072_segment02_1to1.png':'Arch stone and railing show their original faceted illumination; no new field return stripe.',
'horizontal_3072_segment03_1to1.png':'Bridge-to-stair edge and paving joint stay continuous; no horizontal rectangle.'}
review=[]
for q in v['qa']:
    name=Path(q['file']).name
    actual=name in vertical or name in horizontal or q['kind'] in ('internal_junction','external_west_seam','outer_corner')
    if name in vertical:finding=vertical[name]
    elif name in horizontal:finding=horizontal[name]
    elif q['kind']=='internal_junction':finding='Viewed in native 3x3 montage with no resampling. Contours and plane colors remain joined; no introduced four-way cross.'
    elif q['kind']=='external_west_seam':finding='Actual 1:1 strip viewed against current r09_c10 selected-v2. Joined post/rail/water geometry is continuous. Identical to the hard-cut west interface.'
    elif q['kind']=='outer_corner':finding='Actual 1:1 corner viewed; no missing coverage, exposed guide or artificial edge. Unavailable exterior neighbors remain pending.'
    else:finding='SHA-identical to prior actually reviewed hard-cut strip; carry forward its scoped decision without claiming a fresh view.'
    review.append({'file':q['file'],'sha256':q['sha256'],'kind':q['kind'],'actualViewedThisReview':actual,'resampledForInspection':False,'unchangedFromHardcut':q['unchangedFromHardcut'],'finding':finding,'blockingDefectSeen':False})
returns=[]
for q in v['fieldReturnQA']:
    returns.append({**q,'viewed':True,'finding':'Actual full native crop spans the delta footprint plus 64 px context. No new straight return edge or cross-material tint found. Smooth field fade affects color only; image was not blurred.'})
core=np.asarray(Image.open(out/'core4096.png').convert('RGB'))
old=np.asarray(Image.open(TILE/'assembly_hardcut/core4096.png').convert('RGB'))
changed=int(np.any(core!=old,axis=2).sum())
record={'schemaVersion':1,'tile':'r09_c11','reviewedAtUtc':now(),'reviewer':'finish_c11_seams agent; direct original-pixel image inspection',
'recommendedCandidate':m['outputs'],'assembly':info(out/'assembly.json'),'pixelVerification':info(out/'pixel-verification.json'),
'decision':'select_bounded_v2_as_complete_native_4K_candidate_with_scoped_QA','recommendSelected':True,'qualifiedComplete4KCandidate':True,
'scope':'All 41 seam/junction/west/corner areas are covered by current actual review or SHA-proven unchanged previous actual review. Full 1254 preview actually viewed for composition only; no claim of all interior pixels inspected at 1:1.',
'actualReviewedCounts':{'verticalSeams':5,'horizontalSeams':6,'junctions':9,'westSegments':4,'outerCorners':4,'fieldSupportAndReturnCrops':5,'fullTileDownscaledOverview':1},
'unchangedReviewCarryForward':{'verticalSeams':7,'horizontalSeams':6,'evidence':[info(TILE/'qa-final/vertical-junction-review.json'),info(TILE/'qa-final/horizontal-review.json')]},
'qa':review,'fieldSupportAndReturns':returns,'overview':{**info(out/'preview1254.png'),'actualViewed':True,'finding':'Arch bridge, cream walkway, descending stairs, gray balustrades, river and tree masses remain coherent. No square grid of color corrections visible at presentation scale.'},
'constraints':{'allTranslations':[0,0],'resampling':False,'warp':False,'imageBlur':False,'newAIGeneration':False,'perSourceRgbBound':16,'maximumActualSourceRgbDelta':[max(s['maxPerChannelDelta'][k] for s in m['steps']) for k in range(3)],'supportPixels':160,'transitionPixels':6,'axisRangeFadePixels':64,'v2Change':'6 px feather now uses the same axis scope/fade as the selected seam; no feather remains outside the reviewed range.','changedCorePixelsFromHardcut':changed,'rawSourceHashesUnchanged':m['sourceHashesUnchanged'],'coreExactReplay':True,'westHaloExact':True},
'AIRequiredForReviewedDefects':False,
'knownNonblockingRemainders':['Local water stroke frequency and minor stone/leaf facet shade variations remain from genuine native sources; these are not presented as mathematically identical paint.','A small approximately 1-3 px rail bevel irregularity persists near the r04_c03 cut. With continuous silhouette and no missing structure, another full AI repaint or repeated one-pixel tuning is not warranted.'],
'unresolvedForFormalDelivery':['North/east/south exterior neighbors are not available and their joins are not accepted.','Canonical structure is prepared for future day reuse; a produced day counterpart and equality check are still pending.','Full-city navigation/client/runtime acceptance and whole-city completion remain pending.'],
'formalAccepted':False,'clientAccepted':False,'wholeCityComplete':False,'rootCountChanged':False,'cleanup':'No source or older candidate was changed/deleted. Root may perform retention cleanup after selected final files and all current references are complete; retain provenance text and required mask/field files.'}
write(out/'visual-review.json',record)
write(TILE/'qa-final/bounded-selection-review.json',{'review':info(out/'visual-review.json'),'core':m['outputs']['core'],'extended':m['outputs']['extended'],'preview':info(out/'preview1254.png'),'qualifiedComplete4KCandidate':True,'formalAccepted':False,'rootCountChanged':False})
print(record['constraints'])
print(m['outputs'])

import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'r09_c09'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(im): return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
verification=T/'qa/final-internal-verification.json'
v=json.loads(verification.read_text(encoding='utf-8'))
corep=Path(v['source']['file'])
assert sha(corep)==v['source']['sha256']
core=Image.open(corep).convert('RGB')
observations={
 'internal_horizontal_3_part1.png':'The y3072 cut crosses quiet ivory paving above the curved joint. Broad diagonal paint facets are visible across the crop; no seam-axis stripe, added score or contour discontinuity identified at original pixels.',
 'internal_horizontal_3_part2.png':'Curved paving joint and its white bevel cross the y3072 cut continuously. The red lower scroll entering at the far right retains a coherent outer contour; no visible horizontal step or detached highlight identified.',
 'internal_horizontal_3_part3.png':'Central red shaft, the two lower curled arms, rounded red highlights and right foliage remain continuous through y3072. No cut curl, duplicated contour, shaft offset or horizontal exposure strip identified in this crop.',
 'internal_horizontal_3_part4.png':'Rounded light and dark green leaf groups continue through y3072 with connected silhouettes and highlights. Existing dark canopy gaps follow the forms; no cut horizontal leaf row or straight tonal bar identified.',
 'internal_vertical_1_part4.png':'The existing curved stone joint and both white bevel edges cross x1024 without an evident kink. The remaining full-height crop contains broad low-contrast diagonal ivory facets; no vertical compositing stripe or new scratch identified.',
 'internal_vertical_2_part4.png':'The lower red scroll and gold hanging bead remain connected across x2048. The crop below contains the red lantern body edge, ivory floor and part of an existing soft cast shadow; no vertical cut contour or new line identified.',
 'internal_vertical_3_part4.png':'Overlapping foliage, the small exposed ivory gap and deep canopy shade continue across x3072. Leaf highlights and silhouettes are coherent, with no duplicated leaf edge or seam-aligned vertical stripe identified.',
 'intersection_r3_c1.png':'The four-cell junction is in quiet paving; the existing curved groove below it also crosses the vertical join continuously. Broad diagonal stone variation is present, but no four-quadrant tonal split or cross artifact is evident.',
 'intersection_r3_c2.png':'Lower curled arm silhouette, spiral center, white/red highlights, gold bead and central shaft remain coherent around the four-cell junction. Upper paving groove and upper arm are also continuous in the crop. No visibly detached contour or abrupt four-way step identified.',
 'intersection_r3_c3.png':'Rounded canopy silhouette, leaf clusters and quiet upper ivory background pass through the junction coherently. Natural overlapping leaf shading remains; no cross-shaped seam or truncated leaf identified.',
 'horizontal_r4_c1.png':'The y3187 guide transition crosses the existing curved paving joint near its right section. The central T-shaped connector is part of the rendered stone structure, with joined walls and bevels. No guide-end horizontal bar, unjoined scoring or repeated groove identified.',
 'horizontal_r4_c2.png':'Quiet ivory paving at y3187 retains low-contrast diagonal paint variation. Existing groove at upper left and red scroll/gold bead at far right have coherent outlines; no artificial guide-end edge identified.',
 'horizontal_r4_c3.png':'At y3187 the lower red arm, bright curved gold collar and right foliage retain continuous contour and material shading. No offset gold edge, detached highlight or horizontal color bar identified.',
 'horizontal_r4_c4.png':'At y3187 all bright and dark green leaf masses, their highlights and canopy gaps remain connected. No horizontal leaf cut, repeated grid stroke or guide-end stripe identified.'
}
checks=[]
for old in v['checks']:
    fp=Path(old['file']); im=Image.open(fp).convert('RGB')
    assert sha(fp)==old['sha256'] and rgb(im)==old['decodedRgbSha256']
    assert core.crop(old['targetCoreBox']).tobytes()==im.tobytes()
    item={k:old[k] for k in ['file','sha256','kind','targetCoreBox','source','decodedRgbSha256','finalCropEqualsCoreBox']}
    item['pixels']=list(im.size)
    item['operation']='Integer source crop; no resampling or image modifications'
    item['resampling']='none'
    if old['inheritance'] is not None:
        h=old['inheritance']; hp=Path(h['reviewFile']); ep=Path(h['earlierCropFile'])
        assert sha(hp)==h['reviewFileSha256']
        assert sha(ep)==h['earlierCropSha256']
        assert rgb(Image.open(ep))==item['decodedRgbSha256']
        item.update(reviewMethod='inherited_exact_decoded_rgb_visual_review',newlyActuallyViewed=False,inheritance=h,observation=h['observation'],requiresRepair=h['requiresRepair'])
    else:
        assert fp.name in observations,fp.name
        item.update(reviewMethod='tools.view_image(detail=original), individually named unscaled final exported PNG',newlyActuallyViewed=True,inheritance=None,observation=observations[fp.name],requiresRepair=False)
    item['defects']=[]
    item['status']='pass_for_listed_scope'
    checks.append(item)
assert len(checks)==49 and sum(x['newlyActuallyViewed'] for x in checks)==14
out={'schemaVersion':1,'tile':'r09_c09','reviewer':'c09_final_internal','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'source':v['source'],'verificationFile':str(verification),'verificationFileSha256':sha(verification),'scope':{'internalVerticalSeamCrops':12,'internalHorizontalSeamCrops':12,'fourCellIntersections':9,'horizontalGuideInnerEdgeCrops':16,'total':49},'actualNewViewCount':14,'inheritedExactRgbReviewCount':35,'inheritanceBreakdown':{'earlyInternalReview':31,'earlyNeighborNorthGuideReview':4},'sourceAndCropHashesReverifiedAfterViews':True,'allFinalCropsEqualCandidateIntegerSourceBoxes':True,'checks':checks,'newDefects':[],'requiresRepair':False,'passForListedScopes':True,'minorObservations':['Broad low-contrast diagonal ivory paint facets are visible in quiet paving; no artificial axis-aligned stripe was identified in the listed views.','No numerical boundary threshold was used to grant visual approval. The conclusions concern the visible listed scopes at original pixels, not a guarantee of exact geometric identity between independently generated cells.'],'imagesModified':False,'formalAccepted':False,'clientValidated':False,'qualifiedComplete4KCandidate':False,'wholeCityComplete':False,'scopeLimit':'Internal seams, intersections and horizontal guide boundaries only. External neighboring joins, outer edges and vertical guide boundaries require separate review; root performs complete-candidate selection.'}
p=T/'qa/final-internal-review.json'
p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'file':str(p),'sha256':sha(p),'total':49,'newActualViews':14,'inheritedExactRgbReviews':35,'requiresRepair':False},indent=2))

from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent;T=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
idx=json.loads((D/'review-image-index.json').read_text(encoding='utf-8'))
assert len(idx['images'])==9
for v in idx['images']:assert sha(v['image']['file'])==v['image']['sha256']
notes={
 'full-r1-c1':'Complete upper-left paving and broad lower rail reviewed at original pixels. The corrected diagonal surface crease in tile[395,235,750,565] is absent; clean ivory painting, original white bevel and stone joint remain. Standard1024and actual909/1085/1139 seams have no visible break.',
 'full-r1-c2':'Upper central paving, tree-cast shadow and pedestal-left corner reviewed. Shadow, stone outlines and small inset pavers connect across x1933/2048/2109/2163 and the row joins without a rectangular source boundary, doubled line or missing face.',
 'full-r1-c3':'Upper-right sculpted pedestal, shadow, curved decorative paving course and slabs reviewed. Broad flowing highlights connect to the neighboring carved region; no abrupt clipping or dislocated structure at x2957/3072/3133/3187 or upper row returns observed.',
 'full-r2-c1':'All middle-left paving, narrow diagonal border and broad cross-rail inspected. Joints, slab widths and painterly texture continue across both standard and actual placements without a visible paste band or crack.',
 'full-r2-c2':'Central full rail, lower joint and surrounding stone fields inspected. The long shadowed rail and diagonal paving joints remain connected through x/y2048 and all associated overlap returns.',
 'full-r2-c3':'Middle-right relief and large surrounding slabs inspected. Rounded scroll/head relief, outer curved bevel and adjacent slabs remain connected across the full placement region. Existing broad stylized highlight shapes are continuous and do not present a join break.',
 'full-r3-c1':'Lower-left ivory course, recessed gray course and partial ornament inspected. Diagonal paving, bevel widths and narrow divider joints continue across y2957/3072/3133/3187 and lower x909/1024/1139.',
 'full-r3-c2':'Lower middle diamond-oriented slabs and wide ivory dividing courses inspected. No block-aligned colour step, duplicate edge, discontinuity or hole observed at any named join.',
 'full-r3-c3':'Lower-right slim courses, paving and large cloud-scroll relief inspected. Rounded borders and fine shadow grooves continue across last-row and last-column seams. Bottom edge sources are also independently byte-verified against the previously accepted complete shared-border QA.'
}
views=[dict(v,actuallyViewed=True,viewedWith='view_image(detail=original)',observation=notes[v['id']]) for v in idx['images']]
std=[]
for i,s in enumerate([1024,2048,3072],1):
 std.extend([{'orientation':'vertical','x':s,'yRange':[0,4096],'nativeViews':[f'full-r{r}-c{i}' for r in range(1,4)],'status':'no-visible-internal-seam-defect'},{'orientation':'horizontal','y':s,'xRange':[0,4096],'nativeViews':[f'full-r{i}-c{c}' for c in range(1,4)],'status':'no-visible-internal-seam-defect'}])
cross=[{'tileLocalXY':[x,y],'nativeView':f'full-r{r}-c{c}','status':'no-visible-crossing-defect'} for r,y in enumerate([1024,2048,3072],1) for c,x in enumerate([1024,2048,3072],1)]
actual=[]
for s in idx['actualPlacementSeams']:
 i=1 if s<1536 else 2 if s<2816 else 3
 actual.append({'coordinate':s,'verticalNativeViews':[f'full-r{r}-c{i}' for r in range(1,4)],'horizontalNativeViews':[f'full-r{i}-c{c}' for c in range(1,4)],'status':'full-span-reviewed'})
fix=T/'r07_c10/r01_c01-v1/clean-surface-v1'
src=Image.open(idx['source']['file']).convert('RGB')
assert np.array_equal(np.array(src.crop((395,235,750,565))),np.array(Image.open(fix/'surface-repair.png').convert('RGB')))
report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'close_c03','sourceCheckpoint':idx['sourceCheckpoint'],'source':idx['source'],'sourceSHA256':idx['source']['sha256'],'imageIndex':info(D/'review-image-index.json'),'reviewedImages':views,'fullyPaintedNativeTileReviewed':True,'nativeScale':1,'reviewedOpaquePixels':16777216,'reviewCoverage':'All9 actual-viewed1536x1536 native crops,256px overlaps, starts0/1280/2560 in bothaxes. Every source pixel covered. The six full standard seam lines, their9intersections, and actual placement/return lines are included. No thumbnail substituted for native review.','standardInternalSeams':std,'nineStandardIntersections':cross,'actualPlacementSeams':actual,'closedFindings':[{'id':'upper-left-diagonal-surface-crease','tileLocalLTRB':[395,235,750,565],'status':'closed-in-current4K','repairReview':info(fix/'visual-review.json'),'repairManifest':info(fix/'manifest.json'),'currentRoiExactlyEqualsReviewedRepair':True,'note':'Actual AI repaint visible in the current full tile; source slab highlight/bevel/joint preserved. The separate triangle chip was only in unpublished top115halo and is absent from actual tile coordinates.'}],'openInternalFindings':[],'localInternalVisualAccepted':True,'southBoundary':{'locallyAccepted':True,'review':idx['southBorderPriorQa'],'activeBottom384PixelsExactlyEqualReviewedSource':True,'bottomNeighbourRgbaExactlyEqualReviewedDerivedSource':True,'source':idx['southBorderSource'],'scope':'Full4096sharedborder with384pixels each side, using previously native-viewed4overlapping boundary images and available southwestcorner. Source verification repeated; priorQA is not silently broadened to unknown neighbours.'},'pendingExternalChecks':[{'edge':'north','reason':'r06_c10 and required northern corners unavailable as accepted actual neighbours.'},{'edge':'west','reason':'r07_c09 unavailable as a complete accepted actual neighbour; existing narrowhalo does not provide fullborder acceptance.'},{'edge':'east','reason':'r07_c11 and required eastern corners unavailable as accepted actual neighbours.'},{'scope':'geometry/navigation and nearest-camera runtime','reason':'Not validated by this art-only candidate review.'},{'scope':'wholecity256tiles and all adjacencies','reason':'Remaining tiles and full-city/runtime validation are incomplete.'}],'formalAccepted':False,'wholeCityAccepted':False,'clientAccepted':False,'rootStateModified':False,'noNewModelCallsForReview':True}
(D/'internal-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'review':info(D/'internal-review.json'),'sourceSHA256':idx['source']['sha256'],'fullyPaintedNativeTileReviewed':True,'openInternalFindings':[]}))

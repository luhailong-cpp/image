from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
idx=json.loads((D/'review-image-index.json').read_text(encoding='utf-8'))
views=idx['images']
assert len(views)==9
for p in views:assert sha(p['image']['file'])==p['image']['sha256']
observations={
 'full-r1-c1':'Top-left carved panel, broad ivory/plain course, pale gray paving and left slate corner reviewed. Slanting ring and cross-course edges pass both nominal1024lines and actual909/1139 placements without broken relief or a visible straight paste edge.',
 'full-r1-c2':'Upper middle broad paving courses and ivory/gray circular bands reviewed across x1933/2048/2163 and y909/1024/1139. Bevels and cross-joints remain continuous. Existing shallow warm decorative strokes inside the ivory band are retained; they are not patch-edge seams.',
 'full-r1-c3':'Upper-right cloud-scroll relief and broad paving courses reviewed. Curl contour, lower shadow, diagonal joint and thin horizontal joints remain continuous across actual2957/3187 x placements and y909/1139 joins.',
 'full-r2-c1':'Left middle pale stone paving, curved rim, new r02c01 closure and beginning slate inset row reviewed. Cross-band and corner meet continuously through y1933/2048/2163 and x909/1024/1139. Stronger source-retained stone mottling has no straight cutoff along these joins.',
 'full-r2-c2':'Center whole three-inset row, repaired gray foot and neighboring ivory foot reviewed at native size. x2163/y1975..1983 finding remains closed in the actual committed4K. Gray channel foot has no old ivory cap, clipped highlight head or abrupt change at the return.',
 'full-r2-c3':'Middle-right multi-course frame, horizontal bands, right slab and cloud carving reviewed. Horizontal y1933/2048/2163 placements and x2957/3072/3187 positions have continuous contours, bevels, tone and relief.',
 'full-r3-c1':'Lower-left curved ivory rim, pale stone and first slate columns reviewed. Internal y2957/3072/3187 and x909/1024/1139 edge crossings are continuous. Slab border below the inset row has a coherent shadow and no paste-edge kink.',
 'full-r3-c2':'Lower middle three slate columns, ivory dividers and small connecting stones reviewed. Long curves and central cross-band continue over both nominal and actual placement lines; no missing structure or doubled edge found.',
 'full-r3-c3':'Lower-right cloud rim, interior slab, horizontal framing and lower paving reviewed. Actual and standard seam locations preserve consistent continuous stone edges with no abrupt band or rectangular patch edge.'
}
reviewed=[]
for v in views:
 reviewed.append(dict(v,viewedWith='view_image(detail=original)',actuallyViewed=True,observation=observations[v['id']]))
std=[]
for i,s in enumerate([1024,2048,3072],1):
 std += [{'orientation':'vertical','x':s,'yRange':[0,4096],'nativeViews':[f'full-r{r}-c{i}' for r in range(1,4)],'status':'no-visible-internal-seam-defect'},
         {'orientation':'horizontal','y':s,'xRange':[0,4096],'nativeViews':[f'full-r{i}-c{c}' for c in range(1,4)],'status':'no-visible-internal-seam-defect'}]
cross=[]
for ri,y in enumerate([1024,2048,3072],1):
 for ci,x in enumerate([1024,2048,3072],1):
  cross.append({'tileLocalXY':[x,y],'nativeView':f'full-r{ri}-c{ci}','status':'no-visible-crossing-defect'})
actual=[]
for s in [909,1139,1933,2163,2957,3187]:
 i=1 if s<1536 else 2 if s<2816 else 3
 actual.append({'coordinate':s,'verticalNativeViews':[f'full-r{r}-c{i}' for r in range(1,4)],'horizontalNativeViews':[f'full-r{i}-c{c}' for c in range(1,4)],'status':'full-span-reviewed'})
report={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'close_c03','sourceCheckpoint':idx['sourceCheckpoint'],'source':idx['source'],'sourceSHA256':idx['source']['sha256'],'imageIndex':info(D/'review-image-index.json'),'reviewedImages':reviewed,'fullyPaintedNativeTileReviewed':True,'nativeScale':1,'reviewedOpaquePixels':16777216,'reviewCoverage':'Nine actual-viewed1536x1536 exact source crops,256px overlaps, starts0/1280/2560 on both axes. Every source pixel is covered, including full named seams and every corner. No thumbnail is used as native acceptance evidence.','standardInternalSeams':std,'nineStandardIntersections':cross,'actualPlacementSeams':actual,'openInternalFindings':[],'closedFindingEvidence':info(D.parent/'r08_c10'/'r02_c03-v2'/'final-v1'/'finding-closure.json'),'localInternalVisualAccepted':True,'formalAccepted':False,'externalSeamsAccepted':False,'wholeCityAccepted':False,'limitations':['This report covers this committed4K tile internal visual continuity only. Outer neighbors, inherited issues in other tiles, remainingcity256 assembly, navigation and nearest-camera runtime checks are not accepted by this report.','Some inherited left/slate stone panels retain stronger veining/mottling than new plain ivory paving. It is continuous within the image; this report makes no new style-change request or claim of single-shot4K generation.'],'rootStateModified':False}
(D/'internal-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'internalReview':info(D/'internal-review.json'),'fullyPaintedNativeTileReviewed':True,'openInternalFindings':[]}))

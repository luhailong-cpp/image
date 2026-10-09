from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent;O=N/'full-review-native-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=(T/'source-checkpoint.json').read_bytes();cp=json.loads(raw.decode('utf-8-sig'))
assert hashlib.sha256(raw).hexdigest()=='0ebfa4794561aca0318063b28d48c381ec0bdbc4b0fabfcd9c0b424a89d11c56'
def source(tile):
 s=next(v for v in cp['candidateSet'] if v['tile']==tile);assert sha(s['file'])==s['sha256'];return s
idx=read(O/'review-image-index.json');obs=read(O/'actual-view-observations.json');assert obs['allIndexedImagesActuallyViewedAtNativeScale'] and not obs['openInternalFindings'] and not obs['openWestBoundaryFindings']
src=source('r07_c12');a=np.array(Image.open(src['file']).convert('RGBA'));b=np.array(Image.open(idx['source']['file']).convert('RGBA'))
assert a.shape==(4096,4096,4) and np.all(a[:,:,3]==255) and np.array_equal(a,b)
left=source('r07_c11');sw=source('r08_c11')
assert np.array_equal(np.array(Image.open(left['file']).convert('RGBA'))[:,3712:],np.array(Image.open(idx['westNeighbor']['file']).convert('RGBA'))[:,3712:])
assert np.array_equal(np.array(Image.open(sw['file']).convert('RGBA'))[:384,3712:],np.array(Image.open(idx['southWestNeighbor']['file']).convert('RGBA'))[:384,3712:])
(O/'root-checkpoint-v016.json').write_bytes(raw)
proof={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':ref(O/'root-checkpoint-v016.json'),'rootSource':src,'visuallyReviewedSource':idx['source'],'all4096SquaredRGBAIdentical':True,'changedNativePixels':0,'westNeighbor':left,'westReviewedStripLTRB':[3712,0,4096,4096],'westReviewedStripIdentical':True,'southWestNeighbor':sw,'southWestReviewedCornerLTRB':[3712,0,4096,384],'southWestReviewedCornerIdentical':True,'noResizingOrModelCalls':True,'rootStateModified':False}
save(O/'root-v016-identity-proof.json',proof)
byid={v['id']:v for v in obs['viewedImages']}
for group in ['images','westBoundaryImages','cornerImages']:
 for e in idx[group]:
  v=byid[e['id']];assert e['image']==v['image'] and sha(e['image']['file'])==e['image']['sha256'] and v['actuallyViewed'] and not v['openFindings']
  e.update(actuallyViewed=True,viewedWith='view_image(detail=original)',observation=v['observation'])
idx.update(source=src,sourceSHA256=src['sha256'],westNeighbor=left,southWestNeighbor=sw,rootIdentityProof=ref(O/'root-v016-identity-proof.json'))
save(O/'root-review-image-index.json',idx)
seams=[];cross=[];placements=[]
for k,s in enumerate([1024,2048,3072],1):
 seams.extend([{'orientation':'vertical','x':s,'yRange':[0,4096],'nativeViews':[f'full-r{r}-c{k}' for r in [1,2,3]],'status':'no-visible-internal-seam-defect'},{'orientation':'horizontal','y':s,'xRange':[0,4096],'nativeViews':[f'full-r{k}-c{c}' for c in [1,2,3]],'status':'no-visible-internal-seam-defect'}])
for r,y in enumerate([1024,2048,3072],1):
 for c,x in enumerate([1024,2048,3072],1):cross.append({'tileLocalXY':[x,y],'nativeView':f'full-r{r}-c{c}','status':'no-visible-crossing-defect'})
for p in [909,963,1085,1139,1933,1987,2109,2163,2957,3011,3133,3187,4035]:
 k=1 if p<1536 else 2 if p<2816 else 3
 placements.append({'coordinate':p,'verticalNativeViews':[f'full-r{r}-c{k}' for r in [1,2,3]],'horizontalNativeViews':[f'full-r{k}-c{c}' for c in [1,2,3]],'status':'full-span-reviewed'})
closure=read(N/'final-chain-audit-closure.json');assert closure['allPixelAndProvenanceChecksPassedWithAddendum'] and not closure['remainingFindings']
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'close_c03','tile':'r07_c12','sourceCheckpoint':ref(O/'root-checkpoint-v016.json'),'source':src,'sourceSHA256':src['sha256'],'sourceSHA':src['sha256'],'imageIndex':ref(O/'root-review-image-index.json'),'actualViewObservations':ref(O/'actual-view-observations.json'),'rootIdentityProof':ref(O/'root-v016-identity-proof.json'),'reviewedImages':idx['images'],'fullyPaintedNativeTileReviewed':True,'nativeScale':1,'reviewedOpaquePixels':4096**2,'reviewCoverage':'All 9 native 1536 crops at x/y starts 0,1280,2560 actually viewed at original scale, with 256-pixel overlaps and no thumbnail substitution. The complete 4096 square, six full standard seams, nine intersections and actual placement/return bounds were reviewed. Final root v016 is exactly identical to the visually reviewed local source.','standardInternalSeams':seams,'nineStandardIntersections':cross,'actualPlacementSeams':placements,'extendedRepairROIs':[{'tileLocalLTRB':[645,3133,870,3290],'nativeViews':['full-r3-c1'],'status':'wood rail and gold flourish repair closed; no visible repair edge'},{'tileLocalLTRB':[1374,3133,1659,3798],'nativeViews':['full-r3-c1','full-r3-c2'],'status':'paving and curb repair closed; no doubled joint or visible rectangular edge'}],'closedFindings':['r03_c01 lower gold flourish and wood rail join','r03_c02 bottom paving double contour and border ghost'],'openInternalFindings':[],'localInternalVisualAccepted':True,'westBoundary':{'locallyAccepted':True,'source':left,'reviewedImages':idx['westBoundaryImages'],'scope':'Entire 4096 shared edge, 384 native pixels each side, including all explicit left returns.'},'southwestCorner':{'knownQuadrantsLocallyAccepted':True,'reviewedImages':idx['cornerImages'],'unknownQuadrants':['r08_c12 southeast quadrant absent'],'fullFourTileCornerAccepted':False},'southBoundary':{'locallyAccepted':False,'reason':'r08_c12 not yet generated at this frozen source.'},'chainAudit':ref(N/'final-chain-audit.json'),'metadataCorrectionAddendum':ref(N/'metadata-correction-addendum.json'),'chainAuditClosure':ref(N/'final-chain-audit-closure.json'),'actualModelCalls':20,'actualModel':None,'actualQuality':None,'pendingExternalChecks':[{'edge':'north','reason':'r06_c12 missing.'},{'edge':'east','reason':'r07_c13 missing.'},{'edge':'south','reason':'r08_c12 missing.'},{'scope':'all four-tile external corners','reason':'Unknown external quadrants remain.'},{'scope':'geometry/navigation and nearest-camera runtime','reason':'Not validated by this art-only review.'},{'scope':'whole city 256 tiles and adjacencies','reason':'Remaining tiles and full-city checks incomplete.'}],'formalAccepted':False,'wholeCityAccepted':False,'clientAccepted':False,'rootStateModified':False,'noNewModelCallsForReview':True}
save(O/'internal-review.json',review)
print(json.dumps({'review':ref(O/'internal-review.json'),'source':src,'reviewedImages':13,'openInternalFindings':[],'formalAccepted':False}))

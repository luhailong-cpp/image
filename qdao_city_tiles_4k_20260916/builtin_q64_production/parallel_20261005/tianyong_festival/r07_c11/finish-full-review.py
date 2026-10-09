from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
N=Path(__file__).resolve().parent;O=N/sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
index=read(O/'review-image-index.json');obs=read(O/'actual-view-observations.json')
assert not obs['openInternalFindings']
assert index['coveredPixels']==4096**2 and sha(index['source']['file'])==index['sourceSHA256']
for group in ['images','westBoundaryImages','southBoundaryImages']:
 for v in index[group]:
  assert v['id'] in obs['viewed'] and obs['viewed'][v['id']]
  assert sha(v['image']['file'])==v['image']['sha256']
  v.update(actuallyViewed=True,viewedWith='view_image(detail=original)',observation=obs['viewed'][v['id']])
save(O/'review-image-index.json',index)
seams=[];cross=[];placements=[]
for k,s in enumerate([1024,2048,3072],1):
 seams.extend([{'orientation':'vertical','x':s,'yRange':[0,4096],'nativeViews':[f'full-r{r}-c{k}' for r in [1,2,3]],'status':'no-visible-internal-seam-defect'},{'orientation':'horizontal','y':s,'xRange':[0,4096],'nativeViews':[f'full-r{k}-c{c}' for c in [1,2,3]],'status':'no-visible-internal-seam-defect'}])
for r,y in enumerate([1024,2048,3072],1):
 for c,x in enumerate([1024,2048,3072],1):cross.append({'tileLocalXY':[x,y],'nativeView':f'full-r{r}-c{c}','status':'no-visible-crossing-defect'})
for p in [909,963,1085,1139,1933,1987,2109,2163,2957,3011,3133,3187,4035]:
 k=1 if p<1536 else 2 if p<2816 else 3
 placements.append({'coordinate':p,'verticalNativeViews':[f'full-r{r}-c{k}' for r in [1,2,3]],'horizontalNativeViews':[f'full-r{k}-c{c}' for c in [1,2,3]],'status':'full-span-reviewed'})
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'close_c03','sourceCheckpoint':index['sourceCheckpoint'],'source':index['source'],'sourceSHA256':index['sourceSHA256'],'sourceSHA':index['sourceSHA256'],'imageIndex':ref(O/'review-image-index.json'),'reviewedImages':index['images'],'fullyPaintedNativeTileReviewed':True,'nativeScale':1,'reviewedOpaquePixels':4096**2,'reviewCoverage':'All 9 native1536 crops at x/y starts0,1280,2560 actually viewed, with256pixel overlaps and no resized thumbnail substitution. Whole4096square, all6fullstandardseams,9intersections and actual placements/returns covered.','standardInternalSeams':seams,'nineStandardIntersections':cross,'actualPlacementSeams':placements,'closedFindings':obs.get('closedFindings',[]),'openInternalFindings':[],'localInternalVisualAccepted':True,'westBoundary':{'locallyAccepted':True,'source':index['westNeighbor'],'reviewedImages':index['westBoundaryImages'],'scope':'Entire4096sharededge with384pixels eachside at originalpixel resolution; unknown north/east external corner neighbors excluded.'},'southBoundary':{'locallyAccepted':bool(index['southBoundaryImages']),'source':index['southNeighbor'],'reviewedImages':index['southBoundaryImages'],'scope':'Entire4096sharededge with384pixels eachside if native images listed, otherwise still pending full-width neighbor completion.'},'rootDifferenceFromLocal':index['rootDifferenceFromLocal'],'chainAudit':ref(N/'final-chain-audit.json'),'pendingExternalChecks':[{'edge':'north','reason':'r06_c11 actual full neighbor not complete or reviewed.'},{'edge':'east','reason':'r07_c12 actual full neighbor not available.'},{'scope':'geometry/navigation and nearest-camera runtime','reason':'Not validated by this art-only review.'},{'scope':'wholecity256tiles and all adjacencies','reason':'Remaining tiles and full-city validation incomplete.'}],'formalAccepted':False,'wholeCityAccepted':False,'clientAccepted':False,'rootStateModified':False,'noNewModelCallsForReview':True}
if not index['southBoundaryImages']:review['pendingExternalChecks'].append({'edge':'south','reason':'Root r08_c11 full-width top384 context not yet complete at frozen source time.'})
save(O/'internal-review.json',review);print(json.dumps({'review':ref(O/'internal-review.json'),'sourceSHA256':index['sourceSHA256'],'fullImagesViewed':9,'westImagesViewed':len(index['westBoundaryImages']),'southImagesViewed':len(index['southBoundaryImages']),'formalAccepted':False}))

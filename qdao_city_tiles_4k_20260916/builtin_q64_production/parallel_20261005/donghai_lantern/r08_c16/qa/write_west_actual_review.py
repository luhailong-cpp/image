import json, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
B=json.loads((ROOT/'qa/west-final-review-binding.json').read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for k in ('candidate','extendedContext','manifest'):
    assert sha(B[k]['file']) == B[k]['sha256'], (k,'changed')
assert len(B['qa']) == 29
for q in B['qa']: assert sha(q['file']) == q['sha256'],q['file']
findings=[
{'id':'W01','type':'shared-boundary-material-tone','severity':'visible-return-needs-repair','tileRectsXYXY':[[-40,0,100,780]],'preciseDescription':'Actual c15/c16 boundary x=0 has a vertical tint/brushwork change through top water, upper timber crossbeam and blue canopy. Geometry and rope contours remain aligned. Assess material-specific transition on c16 side; preserve immutable c15.','qaIndices':[0,1,20]},
{'id':'W02','type':'shared-boundary-material-tone','severity':'visible-return-needs-repair','tileRectsXYXY':[[-40,1450,100,1750],[-40,2520,100,3650]],'preciseDescription':'At x=0 the continuous diagonal timber rail, exterior blue panel and lower hull wood retain vertical light/tint steps. Several posts naturally coincide with the boundary; do not treat those actual structural edges as defects.','qaIndices':[5,6,10,11,15,16,21,22,23]},
{'id':'W03','type':'shared-boundary-existing-reflection-return','severity':'visible-return-needs-repair','tileRectsXYXY':[[-120,3650,180,4096]],'preciseDescription':'Existing gold/purple water reflections on immutable c15 abruptly lose their continuation at x=0 into the c16 blue water. This concerns matching existing reflected marks, not inventing new light sources or reflected objects.','qaIndices':[15,16,19,23]},
{'id':'W04','type':'internal-timber-color-islands','severity':'visible-patch-edge-needs-repair','tileRectsXYXY':[[665,1780,815,1950],[55,2120,265,2290]],'preciseDescription':'Two timber faces carry orange color islands with jagged edges crossing otherwise continuous brushwork. Rail silhouettes are continuous.','qaIndices':[5,7,9,10,13,25],'diagnostic':'upper-timber-and-blue-floor.png'},
{'id':'W05','type':'internal-blue-plank-mask-artifacts','severity':'visible-patch-edge-needs-repair','tileRectsXYXY':[[675,2150,845,2540],[380,2700,625,2915]],'preciseDescription':'Inner blue planks show jagged tint changes and a dark granular triangle by the lower rail. Exterior blue panel shows a diagonal polygon tint patch with granular upper edge. Board outlines and lantern rope remain continuous.','qaIndices':[7,9,10,12,15,17,18,26],'diagnostics':['upper-timber-and-blue-floor.png','blue-panel-patches.png']},
{'id':'W06','type':'hull-blue-material-return','severity':'visible-return-needs-repair','tileRectsXYXY':[[1810,2890,1870,3150],[2220,2890,2270,3150]],'preciseDescription':'Within the hull-pair overlap, the continuous curved blue band shows left and right nearly vertical jagged color steps. Curved gold borders remain geometrically smooth.','qaIndices':[27],'diagnostic':'hull-blue-join-returns.png'},
{'id':'W07','type':'water-color-return','severity':'visible-return-needs-repair','tileRectsXYXY':[[2895,950,2960,1370]],'preciseDescription':'The reviewed water-pair left return has a nearly vertical scalloped tint/reflection boundary. Rect covers observed diagnostic extent only, not the full water insertion support.','qaIndices':[28],'diagnostic':'water-join-left-return.png'},
{'id':'W08','type':'west-water-right-return-tone','severity':'visible-return-for-consolidated-review','tileRectsXYXY':[[550,3710,690,4096]],'preciseDescription':'Near the right return of west s4, broad blue water planes meet at a nearly vertical jagged tint edge around x=600. Review with the consolidated water repair so this is not accidentally accepted as a seamless return.','qaIndices':[17,19]}
]
notes={
0:'Full actual pair confirms W01; no contour displacement.',
1:'Actual shared edge confirms W01.',
2:'Rope/timber right return continuous; no identified issue in this window.',
3:'Top cropped return has calm water and no newly invented objects; x=0 matching is judged in actual pair windows.',
4:'Lower return post, rail and support continuous; no identified structural break.',
5:'Actual shared rail tone W02 and timber patch W04.',
6:'Continuous diagonal rail has W02; true post edges remain intentional.',
7:'Right return intersects W04 and W05; no rail contour shift.',
8:'Top source return geometry continuous; no identified issue in this window.',
9:'Bottom return shows timber patch and blue tint footprint W04/W05.',
10:'Full pair confirms W02 and local timber/blue material patches W04/W05.',
11:'Shared blue/wood color step W02, outlines aligned.',
12:'Right return shows jagged/ granular blue plank patches W05.',
13:'Top return includes lower timber color island W04.',
14:'Lantern lower body/timber return continuous; no identified issue in this window.',
15:'Full pair confirms hull boundary and lower reflections W02/W03; blue-panel patch W05.',
16:'Shared hull tone/reflection boundary W02/W03.',
17:'Right return blue panel footprint W05 and lower water tint edge W08.',
18:'Top return exterior blue panel patch W05.',
19:'Bottom water includes truncated reflection return W03 and right-edge tint W08.',
20:'Full upper shared edge confirms W01; geometry continuous.',
21:'Mid shared edge confirms diagonal rail tone W02.',
22:'Lower shared edge confirms blue panel/wood tone W02; post/rope geometry intact.',
23:'Bottom shared edge confirms hull tone and existing reflected-mark return W02/W03.',
24:'Complete west 1-2 overlap passes: timber, water and rope contours continuous without a horizontal join.',
25:'Complete west 2-3 overlap has timber patch W04, not geometry mismatch.',
26:'Complete west 3-4 overlap has panel patch W05; lantern contour continuous.',
27:'Complete hull overlap has left/right blue-band color edges W06; wood and gold contours continuous.',
28:'Complete water overlap has left return color boundary W07.'
}
entries=[]
for i,q in enumerate(B['qa']):
    ids=[x['id'] for x in findings if i in x['qaIndices']]
    entries.append({'index':i,'file':q['file'],'sha256':q['sha256'],'pixels':q['pixels'],'actualTileAndHaloRectXYXY':q['actualTileAndHaloRectXYXY'],'sourceCanvas':q['sourceCanvas'],'reviewMethod':'tools.view_image(detail=original); actual visible raster reviewed at native pixel dimensions','actualVisualReview':True,'resized':False,'findingIds':ids,'result':'needs-local-material-return-repair' if ids else 'pass-within-window','notes':notes[i]})
D=ROOT/'repairs/approved-sync/qa/west-review-diagnostics'
diags=json.loads((D/'manifest.json').read_text(encoding='utf-8'))
for q in diags:
    assert sha(q['file'])==q['sha256']
    q['actualVisualReview']=True
    q['reviewMethod']='tools.view_image(detail=original)'
review={'schemaVersion':1,'reviewedUtc':'2026-10-09T04:20:51Z','reviewer':'c14_shared_edge','status':'complete-actual-review-local-color-repairs-required','candidate':B['candidate'],'extendedContext':B['extendedContext'],'manifest':B['manifest'],'assignedCount':29,'actualViewedCount':29,'missingActualViews':[],'allFilesRehashedAfterReview':True,'geometryDisplacementIdentified':False,'formalSeamAccepted':False,'scope':'west-only-joint s1..s4 full+4returns; four complete shared-edge parts; all five repair joins','unmodifiedFinalPixels':True,'coordinateSystem':'c16 tile pixels; x<0 is immutable c15 right edge; c16 x0 equals pair x4096; rects are XYXY and targeted visual defect bounds, not full masks','findings':findings,'qa':entries,'diagnosticActualViews':diags,'recommendedNextStep':'Consolidate overlapping findings with root and finish. Preserve geometry and immutable c15; attempt scoped material color/brush transitions with the documented cumulative RGB24 constraint, then actual-view every affected return. A numeric cap is not evidence the visible issue is solved. Do not regenerate whole tiles or unreviewedly claim pass.'}
out=ROOT/'repairs/approved-sync/qa/review-west-and-joins.json'
out.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out),'actualViewedCount':len(entries),'findings':len(findings),'status':review['status']}))


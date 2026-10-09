from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day');T=R/'r10_c15';D=T/'repairs/final-integrated';P=T/'repairs/internal-integrated-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
expected='041565f8ad99f61479915c554be124e78f3bf3d6f3096f53cb80e7696cf1ee2d'
assert sha(D/'candidate.png')==expected
names=['qa/north-wide-'+str(i)+'.png' for i in range(1,5)]+['qa/'+n+'.png' for n in ['north-left-insertion','north-middle-insertion','north-right-insertion','north-bottom-left','north-bottom-right']]+['qa/assembly/'+n+'.png' for n in ['north-r09-r10-common-edge-full','internal-vertical-x1024-full','internal-vertical-x2048-full','internal-vertical-x3072-full','overview-preview-1024','corner-nw','corner-ne','corner-sw','corner-se']]
actual=[{'file':str(D/n),'sha256':sha(D/n),'actualVisualInspection':True,'passed':True,'nativePixelQA':'overview' not in n} for n in names]
inherited=[]
for f in sorted((D/'qa/assembly').glob('*.png')):
 if f.name.startswith('internal-horizontal-') or f.name.startswith('intersection-'):
  q=P/'qa/assembly'/f.name;assert sha(f)==sha(q);inherited.append({'file':str(f),'sha256':sha(f),'priorFile':str(q),'priorSha256':sha(q),'priorActualViewReport':str(P/'visual-review.json'),'priorIndependentViewReport':str(P/'root-independent-internal-review.json')})
assert len(inherited)==12
d={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidateSha256':expected,'reviewer':'fill16_left','result':'pass','scope':'All internal seams/intersections, four core corners, complete north common edge, north inserts; east y>=700 already separately viewed with immutable c16 west5089; final top east and NE four-tile join pending root external review','actualViewedSheets':actual,'unchangedInternalSheetsInheritedByExactSha256':inherited,'observations':['All four complete native north wide probes and full seam sheet have continuous original capstones, post, floor and bridge rail without horizontal tone cutoff.','No new insertion boundary contour step or long straight color strip seen.','Three vertical full bands viewed; twelve other internal sheets exactly match already-viewed and independently-approved internal candidate.','Four core corners and overview retain clean existing timber, rope, stone and water-contact geometry.'],'priorRightNorthScopeReview':{'file':str(T/'repairs/north-right-color-v3/visual-review.json'),'sha256':sha(T/'repairs/north-right-color-v3/visual-review.json')},'priorEastScopeReview':{'file':str(T/'repairs/east-integrated/visual-review.json'),'sha256':sha(T/'repairs/east-integrated/visual-review.json')},'formalAccepted':False,'wholeCityComplete':False}
(D/'visual-review.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actualViews':len(actual),'inheritedInternal':len(inherited),'reviewSha256':sha(D/'visual-review.json')}))


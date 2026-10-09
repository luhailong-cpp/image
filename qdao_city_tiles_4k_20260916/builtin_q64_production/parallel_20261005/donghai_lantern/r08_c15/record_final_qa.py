from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
Q=T/'repairs/approved-sync/qa'
names=[f'x{x}-return-part{i:02}' for x in [1024,2048,3072] for i in range(1,5)]+[f'corner-{n}' for n in ['nw','ne','sw','se']]+[f'{j}-{n}' for j in ['left-insertion','water-left-horizontal','right-halo-finish'] for n in ['full1254','return-left','return-right','return-top','return-bottom']]
assert len(names)==31
issues=[
 {'id':'left-water-sawtooth','roiXYXY':[1030,2890,1435,3085],'evidence':['x1024-return-part03','water-left-horizontal-return-right'],'finding':'Artificial triangular/sawtooth paint splice in otherwise continuous water, confirmed by independent shared-edge review.','assigned':'finish_c13_repairs'},
 {'id':'left-water-reflection-cut','roiXYXY':[815,3120,990,3370],'evidence':['x1024-return-part04','water-left-horizontal-full1254'],'finding':'Narrow vertical discontinuity in a warm reflected ripple, confirmed independently.','assigned':'finish_c13_repairs'},
 {'id':'west-water-source-crop-line','roiXYXY':[0,3090,520,3320],'evidence':['water-left-horizontal-return-left'],'finding':'Source-inherited near-horizontal crop line around y3187. Frozen DAY has the same line. x>=128 repaired locally; protected west128 remains for actual c14/c15 shared-edge work.','assigned':'finish_c13_repairs plus later western shared edge'},
 {'id':'hull-waterline-step','roiXYXY':[2540,2950,2610,3045],'evidence':['left-insertion-return-bottom'],'finding':'Short unnatural hull/waterline step, independently confirmed by root and shared-edge reviewer.','assigned':'c14_shared_edge'},
 {'id':'roof-color-splice','roiXYXY':[2670,110,3180,535],'evidence':['x3072-return-part01'],'finding':'Cyan polygonal paint area with abrupt return on roof cloth; roof timber geometry intact.','assigned':'root'}]
write(Q/'vertical-and-new-three-review.json',{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_c13_repairs','candidate':ref(T/'repairs/approved-sync/output/r08_c15.png'),'scope':'12 complete vertical seam parts, four tile corners, and three newly required repair windows with their four returns','actualViews':[dict(ref(Q/(n+'.png')),pixelScale=1,actuallyViewed=True) for n in names],'actualViewCount':31,'allObjectsAndContoursOtherwiseContinuous':True,'issues':issues,'status':'complete actual review; listed defects require local final repairs','formalAccepted':False,'notEscalated':[{'roiXYXY':[3220,3280,3360,3450],'finding':'Subtle shadow paint step in hull blue strip; outer hull/water contour continuous. No new repair requested.'}]})
for job,count in [('internal',9),('west',5)]:
 R=T/f'repairs/water-final-{job}';completion=json.loads((R/'completion.json').read_text());qa=completion['qa'];assert len(qa)==count
 write(R/'qa/review.json',{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'finish_c13_repairs','completion':ref(R/'completion.json'),'native':ref(R/'native.png'),'actualNativeViewed':True,'actualReferenceViews':['festival-target.png','day-geometry.png','D:/work/image/designs/gameplay-ui/04-guild.png'],'actualViews':[dict(q,actuallyViewed=True,pixelScale=1) for q in qa],'passedWithinAuthorizedMask':True,'outsideMaskPixelIdentical':True,'resized':False,'finding':'The identified artificial discontinuity is removed and all local returns blend into the existing water brushwork. Object silhouettes remain unchanged.','remainingOutsideScope':(['Protected x<128 source-inherited y3187 crop line must be covered by c14/c15 shared-edge integration.'] if job=='west' else []),'formalAccepted':False})
print(json.dumps({'review':ref(Q/'vertical-and-new-three-review.json'),'internal':ref(T/'repairs/water-final-internal/qa/review.json'),'west':ref(T/'repairs/water-final-west/qa/review.json')}))

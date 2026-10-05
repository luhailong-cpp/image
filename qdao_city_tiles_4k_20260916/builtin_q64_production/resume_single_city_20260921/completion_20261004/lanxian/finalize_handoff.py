from pathlib import Path
import datetime,hashlib,json

R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Explicit human/model visual observations after opening each native board with view_image.
# This list is not inferred from numeric seam scores.
observed={
 'lanxian_day/r08_c06/x1024-all4096.png':'All four 1024-pixel strips viewed; roof tile profiles and wood edges remain continuous.',
 'lanxian_day/r08_c06/y3072-all4096.png':'All four strips viewed; repaired pink umbrella ribs cross continuously; downstream roof and ridge remain single.',
 'lanxian_day/r08_c06/junctions-nine.png':'All nine 320-square neighborhoods viewed; no displaced or doubled contours at their centers.',
 'lanxian_day/r08_c06/edge-west.png':'All four one-sided edge strips viewed; repaired umbrella silhouette and ribs continuous. Matching missing west neighbor not assessed.',
 'lanxian_spring/r08_c06/x2048-all4096.png':'All four strips viewed; repaired paving grout is continuous, roof/caps below keep single contours.',
 'lanxian_spring/r08_c06/y1024-all4096.png':'All four strips viewed; upper pink canopy white ribs now continuous; roof, post and paving clean.',
 'lanxian_spring/r08_c06/edge-north.png':'All four one-sided strips viewed; target paving line continuous with no new return double edge. Missing north neighbor not assessed.',
 'lanxian_spring/r08_c06/edge-west.png':'All four one-sided strips viewed; upper canopy lines continuous, lower canopy/roof unchanged. Missing west neighbor not assessed.',
 'lanxian_spring/r08_c07/x1024-all4096.png':'All four strips viewed; both repaired top paving bevel gaps are gone; fence, paving and vegetation below remain continuous.',
 'lanxian_spring/r08_c07/edge-north.png':'All four one-sided strips viewed; top grout lines continuous, no new double bevel. Matching missing north neighbor not assessed.'
}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();selections=[];totalChanged=0
for city in ('lanxian_day','lanxian_spring'):
    C=R/city;data=read(C/'current-qa/prepared.json');reviewed=[];pending=[]
    for t in data['tiles']:
        assert sha(t['candidate']['file'])==t['candidate']['sha256']
        assert sha(t['baselineSource']['file'])==t['baselineSource']['sha256']
        for v in t['qa']:
            assert sha(v['file'])==v['sha256']
            if not v['pixelIdenticalToViewedBaseline']:
                key=city+'/'+t['tile']+'/'+Path(v['file']).name;assert key in observed
                v.update({'status':'passed_actual_native_view','actuallyViewedAtFinalReview':True,'observation':observed[key]});reviewed.append(v);totalChanged+=1
            else:v['observation']='The complete native QA board is pixel-identical to the baseline board actually viewed earlier in this task.'
        t['internalSixFullSeamsStatus']='passed: six full 4096-pixel seam lengths reviewed at native pixel scale'
        t['nineJunctionsStatus']='passed: nine native 320-square junction crops'
        t['oneSidedFourEdgesStatus']='reviewed; adjacency approval is individually recorded below'
        row,col=[int(s[1:]) for s in t['tile'].split('_')]
        for side,e in t['fourEdges'].items():
            if e['neighbor'] is None:
                r,c={'north':(row-1,col),'south':(row+1,col),'west':(row,col-1),'east':(row,col+1)}[side]
                e['expectedNeighborTile']=f'r{r:02}_c{c:02}'
                pending.append({'tile':t['tile'],'side':side,'candidateSha256':t['candidate']['sha256'],'expectedNeighborTile':e['expectedNeighborTile'],'reason':'No neighboring selected image in this three-tile scope; inspect both SHA-bound images together when available.'})
    review={'city':city,'reviewedAtUtc':now,'reviewMethod':'Actual original-size view_image inspection of native crop boards, plus byte-exact pixel inheritance for unchanged QA regions. No enlargement and no automatic image acceptance.','baselineBoardsActuallyViewed':35,'changedNativeBoardsActuallyViewed':reviewed,'repairs':[{'tile':t['tile'],'records':t['repairs']} for t in data['tiles'] if t['repairs']],'commonEdgePairs':data['commonEdges'],'missingNeighborBorders':pending,'inScopeResult':'pass for existing three-tile internal seams and their two mutual common edges','notClaimed':['full 65536-square city complete','matching unavailable outside neighbors','pixel-identical day/festival architectural geometry'],'sourceAudit':'Independent read-only check: 105 file/SHA references across four native, assembly and candidate records matched; six historical source SHA unchanged. Historical E:/work/image references resolve through D:/work/image relocation.'}
    write(C/'visual-review.json',review)
    data.update({'status':'current_local_triple_ready_for_continuation','selectionRecordedAtUtc':now,'visualReview':info(C/'visual-review.json'),'scopeComplete':True,'wholeCityComplete':False,'formalCityAccepted':False,'missingNeighborBorders':pending,'newAiGenerationCount':1 if city=='lanxian_day' else 3,'newAiBatchTarget':{'model':'gpt-image-2.5-sunburst','quality':'max','route':'builtin','actualModel':None,'actualQuality':None,'explanation':'Host tool exposes neither model/quality selectors nor returned model/quality; target is not proof of actual model.'},'writeOwnership':'This worker finished this scoped handoff and will no longer write Lanxian; next city tasks should start from these exact candidates.','currentQaPreparedRecord':info(C/'current-qa/prepared.json')})
    for t in data['tiles']:
        for repair in t['repairs']:
            repair['visualReview']=info(C/'visual-review.json')
    write(C/'current-selection.json',data);selections.append(info(C/'current-selection.json'))
assert totalChanged==10
write(R/'handoff-index.json',{'createdAtUtc':now,'selections':selections,'scope':'Two existing triples, six 4096-square images; not full cities.','finishedWritingLanxian':True,'globalSelectionChanged':False,'imagesDeleted':False})
print(json.dumps({'selections':selections,'changedNativeBoardsActuallyViewed':totalChanged,'perCityMissingNeighborBorders':8,'finishedWritingLanxian':True},ensure_ascii=False,indent=2))

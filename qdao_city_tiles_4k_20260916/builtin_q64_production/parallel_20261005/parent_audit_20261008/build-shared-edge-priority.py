from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib,collections,numpy as np
A=Path(__file__).resolve().parent;P=A.parent;B=P.parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
I=read(A/'verified-current-index.json');C=read(A/'shared-edge-priority-crops/manifest.json')
now=datetime.now(timezone.utc).isoformat();assert I['summary']['completePixelCandidateCount']==48
old=B/'resume_single_city_20260921/completion_20261004'
rep=P/'parent_repairs_20261008/current'
R=read(rep/'current-selection.json')
current_reports={
 'town_day_old':old/'lanxian/lanxian_day/visual-review.json',
 'town_spring_old':old/'lanxian/lanxian_spring/visual-review.json',
 'fish_old':old/'donghai/review.json',
 'island_old':old/'penglai/input-and-qa-index.json',
 'tian_old':B/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/qa_v5/visual-review-20260920.json',
 'tian_parent':rep/'final-visual-review.json',
 'day_north_east':P/'lanxian_day/r09_c09/qa/root-final-review.json',
 'spring_south':A/'town/qa-binding-supplement.json',
 'spring_bridge':P/'lanxian_spring/r09_c11/selected/delivery.manifest.json',
 'fish_c10c11':P/'donghai_day/r08_c11/repairs/west-leaf-02/qa/review.json',
 'fish_c11c12':P/'donghai_day/r08_c12/repairs/west-common-edge/integration-qa/integration-review.json',
 'fish_c12c13':P/'donghai_day/tiles/west-integration-r08_c13-manifest.json',
 'fish_c13c14':P/'donghai_day/r08_c14/progress.json',
 'lantern_c11c12':P/'donghai_lantern/r08_c12/west-final/qa/review.json',
 'lantern_c10c11':P/'donghai_lantern/r08_c11/west-final-v2/qa/top-paving-review.json',
 'island_day_registry':P/'penglai_day/tile-manifest.json',
 'island_day_north':P/'penglai_day/r10_c12/repairs/visual-review-v5.json',
 'mid_north12':P/'penglai_mid_autumn/r10_c12/qa/final-local-review.json',
 'mid_new13':P/'penglai_mid_autumn/r10_c13/qa/final-local-review.json',
}
evidence={k:ref(p) for k,p in current_reports.items() if p.exists()}
notes=[]
for r in C['records']:
    assert sha(r['crop']['path'])==r['crop']['sha256']
    mutations=[]
    for s in r['sources']:
        actual=sha(s['path'])
        if actual!=s['sha256']:
            mutations.append({'path':s['path'],'viewedSourceSha256':s['sha256'],'currentSourceSha256':actual})
    if mutations:
        assert r['orientation']=='vertical'
        ia,ib=[Image.open(s['path']).convert('RGB') for s in r['sources']]
        band=Image.new('RGB',(256,4096));band.paste(ia.crop((3968,0,4096,4096)),(0,0));band.paste(ib.crop((0,0,128,4096)),(128,0))
        sheet=Image.new('RGB',(1024,1024))
        for k in range(4):sheet.paste(band.crop((0,k*1024,256,(k+1)*1024)),(k*256,0))
        before=np.array(Image.open(r['crop']['path']).convert('RGB'));after=np.array(sheet)
        assert np.array_equal(before,after),'Concurrent source change affected viewed common edge'
        r['concurrentSourceUpdateTransfer']={'observedAt':now,'sourceMutations':mutations,'exactRGBPixelEqualityToViewedCrop':True,'changedPixels':0,'nativeBandWidth':256,'length':4096,'viewedRGBSha256':hashlib.sha256(before.tobytes()).hexdigest(),'currentRGBSha256':hashlib.sha256(after.tobytes()).hexdigest(),'scope':'Current full-PNG hash changed after view; only this identical native common band inherits the visual review.'}
        for s in r['sources']:s['sha256']=sha(s['path'])
    if r['appearance']=='tianyong_festival' and r['tiles'][0]=='r09_c09':
        repaired=rep/'r09_c09.png';base=Image.open(r['sources'][0]['path']).convert('RGB');final=Image.open(repaired).convert('RGB')
        rect=(3968,0,4096,4096)
        ba=np.array(base.crop(rect));fa=np.array(final.crop(rect));assert np.array_equal(ba,fa)
        r['parentRepairTransfer']={'parentSource':ref(repaired),'parentSelection':ref(rep/'current-selection.json'),'rectLTRB':list(rect),'exactRGBPixelEquality':True,'changedPixels':0,'baseCropRGBSha256':hashlib.sha256(ba.tobytes()).hexdigest(),'parentCropRGBSha256':hashlib.sha256(fa.tobytes()).hexdigest(),'scope':'All 128 rightmost columns of parent r09_c09 equal the viewed child source; this exact band transfers without another view.'}
    r['actualVisualReview']={'viewedAt':now,'method':'tools.view_image(detail=original), saved1024 square contains four packed native strips; no resampling','result':'no_actionable_structural_discontinuity_in_viewed_band','fullLengthPixels':4096,'totalBandWidth':256,'wholeTileAccepted':False,'scopeLimitation':'Only the recorded256-wide common-edge band. Does not accept attachment returns outside band, neighboring edges, full four-tile corner windows, whole tile or city.'}
    if r['appearance']=='donghai_day':
        r['actualVisualReview']['observation']='Paving grooves, rope/wood silhouette and red cloth continue at actual common-edge centers x128/384/640/896. Gray painted patches are irregular rather than a hard common-edge cut. No repair justified in this band.'
        r['actualVisualReview']['existingCropIdentity']='Current crop SHA equals already-exported common-edge-c12-c13-full.png, so this view binds that existing QA board to the current c13 post-stone-repair bytes.'
    elif r['orientation']=='vertical':
        r['actualVisualReview']['observation']='Ivory bevels, grey blocks and carving continue across actual common-edge centers x128/384/640/896; soft broad texture variation visible, with no actionable broken contour in the256-wide band.'
    else:r['actualVisualReview']['observation']='Paving grooves/bevels and foliage cross actual common-edge centers y128/384/640/896 without an actionable structural break. Packing boundaries are not art seams.'
dump(A/'shared-edge-priority-crops/manifest.json',C)
viewed={(r['appearance'],'/'.join(r['tiles'])):r for r in C['records']}
root_occupied={'r08_c07/r08_c08','r08_c07/r09_c07','r08_c08/r08_c09','r08_c08/r09_c08','r08_c09/r09_c09','r09_c07/r09_c08','r09_c08/r09_c09'}
edges=[]
def mark(e,status,note,keys):
    e.update(status=status,interpretation=note,evidence=[evidence[k] for k in keys if k in evidence])
for ap in I['appearances']:
    lookup={e['tileId']:e for e in ap['entries']}
    for ta,ea in lookup.items():
        row,col=int(ta[1:3]),int(ta[5:7])
        for tb,ori in [(f'r{row:02d}_c{col+1:02d}','vertical'),(f'r{row+1:02d}_c{col:02d}','horizontal')]:
            if tb not in lookup:continue
            eb=lookup[tb];key=ta+'/'+tb;app=ap['appearance']
            e={'appearance':app,'tiles':[ta,tb],'orientation':ori,'tilePixels':4096,'sources':[{'path':x['path'],'sha256':x['sha256']} for x in [ea,eb]],'formalAccepted':False,'newImageGenerationJustified':False,'indexEvidenceScope':'Metadata snapshot only unless actualVisualReview exists. Recorded passes are not newly reaccepted.'}
            if (app,key) in viewed:
                v=viewed[(app,key)];mark(e,'new_current_native_band_review_pass','Original-pixel common band actually viewed in this task; no new image repair warranted.',[])
                e['sourceIndexSnapshot']=e['sources'];e['sources']=v['sources']
                e['actualVisualReview']=v['actualVisualReview'];e['crop']=v['crop'];e['currentViewRecord']=ref(A/'shared-edge-priority-crops/manifest.json')
                if 'parentRepairTransfer'in v:e['parentRepairTransfer']=v['parentRepairTransfer']
                if 'concurrentSourceUpdateTransfer'in v:e['concurrentSourceUpdateTransfer']=v['concurrentSourceUpdateTransfer']
            elif app=='tianyong_festival':
                if key in root_occupied:mark(e,'root_owned_local_repairs_excluded_from_new_work','Parent REP scoped repairs already exist; root is refining west-upper-tone. No duplicate review or generation requested. Local QA does not cover the entire4096 edge.', ['tian_parent'])
                else:mark(e,'historical_scope_pass_current_edge_binding_to_transfer','Historical v5 report has reviewed row10/common-boundary scopes. Current full-PNG hashes differ for some row9 sources; establish unchanged band identity before reusing broad acceptance. Do not regenerate merely for missing parent binding.', ['tian_old'])
            elif app=='lanxian_day':
                if key in ['r08_c06/r08_c07','r08_c07/r08_c08']:mark(e,'current_pair_scoped_pass_recorded','Current pair hashes and exact baseline band identity are recorded in commonEdgePairs. No repeat native view requested.', ['town_day_old'])
                elif key in ['r08_c09/r09_c09','r09_c09/r09_c10']:mark(e,'current_pair_scoped_pass_recorded','New r09_c09 final report and external north/east manifests bind the inspected edges and northeast four-tile junction.', ['day_north_east'])
                else:mark(e,'selected_manifest_scoped_qa_reported','Selected delivery manifest and indexed west/north QA chain report scoped review. No new native inspection here; keep minor residual and scope limitations.', [])
            elif app=='lanxian_spring':
                if key in ['r08_c06/r08_c07','r08_c07/r08_c08']:mark(e,'current_pair_scoped_pass_recorded','Current selection source and old exact common-edge QA retained; no repeat inspection requested.', ['town_spring_old'])
                elif key=='r08_c10/r09_c10':mark(e,'current_pair_scoped_pass_recorded_with_minor_residuals','Current SHA-binding supplement exists for north-edge/bridge scopes. Old red-column and gold-line microvariations remain scoped disclosures, not a new break found here.', ['spring_south'])
                elif key=='r09_c10/r09_c11':mark(e,'selected_manifest_scoped_qa_reported','Selected new bridge reports west edge reviewed; north/east/south missing-neighbor scopes remain pending.', ['spring_bridge'])
                else:mark(e,'selected_manifest_scoped_qa_reported_with_minor_residuals','Use the current repair-record and visual-review chain rather than obsolete assembly failure label. Full outer-edge acceptance was not independently established here.', ['spring_south'])
            elif app=='donghai_day':
                if key=='r08_c08/r08_c09':mark(e,'current_pair_scoped_pass_recorded','Both selected PNGs equal pinned old sources; full512-wide shared band passed in report.', ['fish_old'])
                elif key=='r08_c09/r08_c10':mark(e,'historical_scope_pass_current_edge_binding_to_transfer','Old shared band passed, but c10 PNG was later changed near its east side. Bind exact current west band to prior QA before treating historical full-PNG report as current.', ['fish_old','fish_c10c11'])
                elif key=='r08_c10/r08_c11':mark(e,'scoped_pass_recorded_unchanged_edge_transfer_required','WEST-LEAF-02 common-edge pass is recorded; later c11 east repair should not invalidate west pixels, but this task did not repeat its equality transfer.', ['fish_c10c11','fish_c11c12'])
                elif key=='r08_c11/r08_c12':mark(e,'scoped_pass_recorded_unchanged_edge_transfer_required','Integration report passed common edge; newer c12/c13 manifest explicitly preserves c12 left3469 columns. Use this preserved region to transfer c11/c12 QA.', ['fish_c11c12','fish_c12c13'])
                else:mark(e,'unaccepted_current_edge_child_repair_in_progress','New c14 progress explicitly says external-edge review pending; west-common-edge directory is active. Child owns this repair; parent should not duplicate generation.', ['fish_c13c14']);e['ownerReserved']='04 渔村日景地图'
            elif app=='donghai_lantern':
                if key=='r08_c08/r08_c09':mark(e,'current_pair_scoped_pass_recorded','Pinned inherited pair full shared band passed.', ['fish_old'])
                elif key=='r08_c09/r08_c10':mark(e,'historical_scope_pass_current_edge_binding_to_transfer','Old band passed; newer c10 east repair superseded whole-PNG binding. Transfer exact west band before reusing report.', ['fish_old'])
                elif key=='r08_c10/r08_c11':mark(e,'scoped_pass_recorded_with_known_minor_return','West-final scoped work exists. WEST-TOP-LEFT-TAPER at pair[3980,145,4052,217] remains disclosed; do not reopen the passed entire edge solely from the old label.', ['lantern_c10c11','lantern_c11c12'])
                else:mark(e,'current_pair_scoped_pass_recorded','Current west-final c11/c12 shared strip and attachment review bound by selected registry.', ['lantern_c11c12'])
            elif app=='penglai_day':
                if key=='r09_c10/r09_c11':mark(e,'current_pair_scoped_pass_recorded','Both inherited tile hashes unchanged; old common boundary scope recorded.', ['island_old'])
                elif key=='r09_c11/r09_c12':mark(e,'historical_scope_pass_current_edge_binding_to_transfer','c12 was replaced by both-side c12-right repair. Old c11/c12 band passed, but matching current west strip to that evidence is still needed at parent level.', ['island_old','island_day_registry'])
                elif key=='r09_c12/r09_c13':mark(e,'selected_manifest_scoped_qa_reported','Both current tiles are declared local_candidate_visual_review_passed by owning registry; no new cross-tile pixel acceptance in this task.', ['island_day_registry'])
                else:mark(e,'unaccepted_current_edge_child_repair_in_progress','v5 interior review explicitly excludes north seam and x3072 roof edge above y900; north integration is in the child task.', ['island_day_north','island_day_registry']);e['ownerReserved']='06 仙岛日景地图'
            else:
                if key in ['r09_c10/r09_c11','r09_c11/r09_c12']:mark(e,'current_pair_scoped_pass_recorded','Inherited pinned shared-boundary sources retain scoped pass; index missing-label issue is not a new image defect.', ['island_old'])
                elif key=='r09_c12/r10_c12':mark(e,'current_pair_scoped_pass_recorded','Full north4096 strip, return and three junctions reviewed; later local edits leave top256 unchanged.', ['mid_north12'])
                elif key in ['r09_c13/r10_c13','r10_c12/r10_c13']:mark(e,'current_pair_scoped_pass_recorded','New r10_c13 final-local-review binds north/west and27 standard QA crops to current candidate.', ['mid_new13'])
                else:mark(e,'selected_manifest_scoped_qa_reported','Current r09_c13 west-final closure report and edge crops indexed; outside changed west500 explicitly preserved.', [])
            e['qaEvidenceEntriesInIndex']=[{'tile':x['tileId'],'qaStatus':x.get('qaStatus'),'auditSource':x.get('auditSource'),'auditEntryPointer':x.get('auditEntryPointer')} for x in [ea,eb]]
            edges.append(e)
assert len(edges)==48
priority_keys=[('penglai_day','r09_c12/r10_c12'),('donghai_day','r08_c13/r08_c14'),('penglai_day','r09_c11/r09_c12')]
priorities=[]
for rank,(app,key) in enumerate(priority_keys,1):
    e=next(e for e in edges if e['appearance']==app and '/'.join(e['tiles'])==key)
    p={'rank':rank,'appearance':app,'tiles':e['tiles'],'sources':e['sources'],'status':e['status'],'newRepairConfirmedByThisReview':False,'action':'Wait for the owning in-progress cross-tile repair and consume its SHA-bound final QA; do not duplicate generation.' if 'ownerReserved'in e else 'Read-only transfer: compare current c12 west256 to the old reviewed c11/c12 band. If equal, carry QA; if different, inspect only changed scopes before deciding whether a repair exists.','ownerReserved':e.get('ownerReserved'),'evidence':e['evidence']}
    if rank==1:p['specificLocation']='Horizontal y4096 of r09_c12; lower r10_c12 north0..900, especially roof near local x3072. Child v5 explicitly excludes this north band.'
    elif rank==2:p['specificLocation']='Vertical x4096 between c13/c14, full row8 y0..4096. c14 west-common-edge is already generating/assembling.'
    else:p['specificLocation']='Vertical x4096 between c11/c12, current c12 local x0..256; historical report belongs to inherited c12, current c12 is right-revised.'
    priorities.append(p)
out={'schemaVersion':1,'observedAt':now,'sourceIndex':ref(A/'verified-current-index.json'),'scope':'Bounded metadata inventory of the48 existing adjacent pairs among48 selected coordinates; only3 metadata-uncertain edges newly viewed at native scale. No image generation. Not a scan of missing tiles, all artwork pixels or whole city.','statusDefinitions':{'current_pair_scoped_pass_recorded':'Existing selected evidence records the common-edge pass; no redundant view done here.','selected_manifest_scoped_qa_reported':'Owner records scoped QA; parent does not claim it independently verified the whole common band here.','historical_scope_pass_current_edge_binding_to_transfer':'Reviewed baseline exists; verify exact current band identity rather than regenerate a good edge.','unaccepted_current_edge_child_repair_in_progress':'Explicit unresolved current edge, already owned by corresponding production task.','root_owned_local_repairs_excluded_from_new_work':'Root current REP/local active tone scope; exclude duplicate work.','new_current_native_band_review_pass':'Actually viewed now and bound to exact source SHA, only256-wide full4096 common strip.'},'summary':{'selectedCoordinates':48,'existingAdjacentPairs':48,'newNativeCommonBandsActuallyViewed':3,'newActionablePaintDefectsConfirmed':0,'formalAcceptance':False,'statusCounts':dict(collections.Counter(e['status'] for e in edges))},'edges':edges,'priorityFollowups':priorities,'doNotCreateUnnecessaryRepairWork':True,'visualEvidence':ref(A/'shared-edge-priority-crops/manifest.json'),'rootRepairConflictAvoidance':{'excludedPairs':sorted(root_occupied),'westUpperToneActive':True,'parentR09C09EastBandVerifiedUnchanged':True},'recommendation':'No newly inspected band requires repainting. Two highest-value open edges are already being repaired by their owner; the third is a provenance/unchanged-pixel QA transfer task.'}
dump(A/'shared-edge-priority.json',out)
print(json.dumps({'file':str(A/'shared-edge-priority.json'),'sha256':sha(A/'shared-edge-priority.json'),'summary':out['summary'],'parentR09C09EdgeTransferVerified':True},ensure_ascii=False))

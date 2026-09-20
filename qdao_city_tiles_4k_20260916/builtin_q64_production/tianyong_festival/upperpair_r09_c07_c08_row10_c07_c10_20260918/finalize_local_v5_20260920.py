from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
report=read(P/'assembly_v5.json');old=read(P/'assembly_v4.json')
fresh={'internal_h3072.png','quad_boundary_v_half1.png','four-tile-junction.png'}
for e in report['qa']:
    p=Path(e['file']);assert sha(p)==e['sha256']
    if p.name.startswith('left_') or p.name in fresh: e['reviewMethod']='view_image original in current session'
    else:
        parent=P/'qa_v4'/p.name;assert sha(parent)==sha(p),(p,parent)
        e['reviewMethod']='pixel-identical full QA board inherited from reviewed v4';e['parentEvidence']=str(parent)
for e in old['placements']:
    for k in ('native','record','fields'):assert sha(e[k])==e[k+'Sha256']
    rec=read(e['record']);assert sha(rec['sourceOutputPath'])==e['nativeSha256'];assert sha(rec['promptFile'])==rec['promptSha256']
    assert all(sha(r['path'])==r['sha256'] for r in rec['submittedImages'])
roi=read(P/'qa_v4_roi_20260920/crop-manifest.json')
for e in roi:assert sha(e['file'])==e['sha256']
qa={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'local_continuity_review_passed_candidate_only','approvedForRootMerge':True,'assembly':str(P/'assembly_v5.json'),'assemblySha256':sha(P/'assembly_v5.json'),'inheritedVerticalFullSeamReview':str(P/'qa_v4/visual-review-partial-20260919.json'),'v4CompletionReview':{'fullHorizontalSeams':[1024,2048,3072],'quadBoundaryHalfBoards':['v_half1','v_half2','h_half1','h_half2'],'row10FullBoundaries':['c08','c09','c10'],'junctions':['four-tile-junction.png','internal-nine-junctions.png'],'actualOldRepairReturnEdges':roi,'finding':'All pending v4 full seam boards, junctions and all 20 actual ROI return-edge crops inspected at original pixels. A stepped bevel at quad (4093,3015) and lower small interruption at (3748,3746) required two new native edits. Other reviewed structures were continuous.'},'v5VisualEvidence':report['qa'],'overview':str(P/'qa_v5/quad-overview.jpg'),'finding':'Both new small bevel interruptions are continuous after bounded native ROI replacement. All eight new return-edge strips and both full support crops inspected; changed whole internal h3072, shared v boundary and four-tile junction rechecked without a definitive broken contour or hard color band. Other full seam boards verified byte-identical to viewed v4. Natural painted texture differences remain; full-city acceptance is outstanding.','mechanical':{'outsideMasksUnchanged':True,'tileRejoinExact':True,'row10FarRightUnchanged':True,'previousRepairSourcesVerified':5,'newNativeSources1254Opaque':2},'resamplingDisclosure':'Bounded generated-art edge registration max_shift=8; flow, color correction and mask preserved in assembly_v4/v5. No artwork upscaling.','formallyAccepted':False,'wholeCityAccepted':False,'runtimePublished':False,'remainingAcceptance':['all outer neighbors','256 tile complete city','foreground','navigation','nearest camera and movement','device performance']}
f=P/'qa_v5/visual-review-20260920.json';assert not f.exists();f.write_text(json.dumps(qa,indent=2),encoding='utf-8')
candidates=[]
for e in report['files']:
    assert sha(e['path'])==e['sha256'];tile=e['tile'];row=int(tile[1:3]);col=int(tile[5:7])
    candidates.append({'appearance':'tianyong_festival','displayName':'天墉城节庆','tile':tile,'file':Path(e['path']).relative_to(R).as_posix(),'sha256':e['sha256'],'assembly':(P/'assembly_v5.json').relative_to(R).as_posix(),'qa':f.relative_to(R).as_posix(),'pixels':[4096,4096],'finalPixelRectXYWH':[(col-1)*4096,(row-1)*4096,4096,4096],'worldRect':{'x':50+(col-1)*18.75,'z':300-row*18.75,'width':18.75,'height':18.75},'status':'candidate_local_continuity_reviewed_not_runtime_accepted','accepted':False,'runtimePublished':False})
ledger={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'ready_for_root_merge','candidates':candidates,'repairRecords':[Path(e['record']).relative_to(R).as_posix() for e in report['placements']],'newUniqueCandidates':1,'replacementCandidates':5,'newNativeSources':2,'sourceAccountingNote':'All v4 sources are already included in 20260919 source-only merge; only two new v5 records are additions.','runtimePublished':False,'formalAcceptance':False}
lf=P/'ledger-v5-20260920.json';assert not lf.exists();lf.write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8');print(str(lf))

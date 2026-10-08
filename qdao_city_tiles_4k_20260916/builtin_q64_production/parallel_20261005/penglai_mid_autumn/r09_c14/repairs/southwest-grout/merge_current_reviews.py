"""Merge current review evidence after the one-time migration. Default is read-only.

This does not approve scoped acceptance. Generic finalizer remains root-owned.
"""
from pathlib import Path
import argparse,copy,hashlib,json,sys
from PIL import Image
F=Path(__file__).resolve().parent;T=F.parents[1];ROOT=T.parent;S=ROOT/'r10_c14'
sys.path.insert(0,str(ROOT))
from production import read,write,sha,now

def ref(p):return dict(file=str(p),sha256=sha(p))
def key(p):return str(Path(p).resolve()).casefold()
def pixelsha(p):return hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest()
def allitems(d):return [v for field in ['items','mainQA','supplementalQA'] for v in d.get(field,[])]

def build():
    app=read(F/'application.json');proof=read(F/'migration-plan.json');auth=read(F/'root-migration-authorization.json')
    assert app['status']=='applied_pending_root_current_QA_finalization'
    assert sha(T/'output/r09_c14-candidate.png')==proof['proposedNorth']['sha256']
    assert sha(S/'output/r10_c14-candidate.png')==proof['currentSouth']['sha256']
    assert auth['applyAuthorized'] is True
    rows={key(v['canonical']):v for v in proof['qa']}
    assert len(rows)==65 and sum(r['changed'] for r in rows.values())==7
    for r in rows.values():
        assert sha(r['canonical'])==r['newPngSha256']
        assert pixelsha(r['canonical'])==r['newPixelSha256']
        if not r['changed']:
            assert r['exactPixelReuse'] is True and r['exactByteReuse'] is True
            assert r['currentFileSha256']==r['newPngSha256'] and r['currentPixelSha256']==r['newPixelSha256']
    approved={key(v.get('canonical',v['file'])):v for v in auth['items']}
    for v in approved.values():assert v['actuallyViewed'] is True and v['nativeScale']==1 and v['verdict']=='scoped_pass'
    history=F/'history-before-application'
    out={};summary=[]
    for tile in [T,S]:
        candidate=tile/'output'/f'{tile.name}-candidate.png';candidate_ref=ref(candidate)
        tilehistory=history/tile.name/'qa';merged={}
        prior_final=tilehistory/'final-local-review.json'
        finalmap={key(i['file']):i for i in allitems(read(prior_final))} if prior_final.exists() else {}
        for name,flag in [('horizontal-review.json','scopedPass'),('external-review.json','externalScopedPass'),('root-review.json','scopedPass')]:
            oldpath=tilehistory/name;oldreport=read(oldpath);items=[]
            for original in allitems(oldreport):
                k=key(original['file']);old=original;source=oldpath
                # The prior final review binds r09's older root observations to the
                # accepted26ef version via its original exact-reuse evidence.
                if tile==T and name=='root-review.json':old=finalmap[k];source=prior_final
                row=rows.get(k);fresh=approved.get(k);p=Path(old['file'])
                if fresh:
                    assert sha(p)==fresh['sha256']
                    verdict='current_pixels_inspected_neighbor_unverified' if old.get('verdict')=='current_pixels_inspected_neighbor_unverified' else 'scoped_pass'
                    evidence=dict(kind='root_actual_native_scale_inspection',record=ref(F/'root-migration-authorization.json'),reviewedFile=fresh['file'],reviewedFileSha256=fresh['sha256'],canonicalFile=str(p),canonicalFileSha256=sha(p),proposalToCanonicalBytesIdentical=bool(fresh.get('canonical')),newVisualInspectionClaimed=True,currentCanonicalFileDirectlyReViewed=not bool(fresh.get('canonical')))
                    observations='Root actually inspected these exact pixels at original scale and passed; approved proposal bytes equal canonical bytes.' if fresh.get('canonical') else 'Root re-viewed the current963d canonical QA at original scale and passed.'
                else:
                    assert row and not row['changed']
                    assert old.get('actuallyViewed') is True and old.get('nativeScale')==1
                    assert old.get('verdict') in ['pass','scoped_pass','pass_scoped','current_pixels_inspected_neighbor_unverified']
                    assert old.get('sha256')==sha(p)==row['currentFileSha256']
                    verdict='scoped_pass' if old['verdict']=='pass_scoped' else old['verdict']
                    evidence=dict(kind='exact_byte_and_pixel_reuse',record=ref(source),priorCandidateSha256=read(source).get('candidate',{}).get('sha256'),priorQAFileSha256=old['sha256'],currentQAFileSha256=sha(p),priorPixelSha256=row['currentPixelSha256'],currentPixelSha256=row['newPixelSha256'],proof=ref(F/'migration-plan.json'),newVisualInspectionClaimed=False)
                    observations='Prior actual native-scale inspection reused after exact PNG-byte and decoded-pixel equality verification.'
                item=dict(file=str(p),sha256=sha(p),actuallyViewed=True,nativeScale=1,verdict=verdict,observations=observations,appliedToCandidateSha256=candidate_ref['sha256'],visualEvidence=evidence,historicalPriorItem=dict(report=ref(source),item=copy.deepcopy(old)))
                if 'reproduction' in old:item['reproduction']=copy.deepcopy(old['reproduction'])
                if row:item['migrationPixelProof']=dict(proof=ref(F/'migration-plan.json'),changed=row['changed'],currentPixelSha256=row['newPixelSha256'])
                items.append(item)
                if k in merged:assert merged[k]['sha256']==item['sha256']
                merged[k]=item
            report=dict(reviewedAt=now(),candidate=candidate_ref,items=items,issues=[],issueCount=0,formalAccepted=False,navigationVerified=False,clientVerified=False,sourceMigration=ref(F/'application.json'),previousReport=ref(oldpath),rootInspectionAuthorization=ref(F/'root-migration-authorization.json'),migrationProof=ref(F/'migration-plan.json'),unchangedQAAcrossTwoTiles=58,changedQAAcrossTwoTiles=7,finalRootApprovalPending=True)
            report[flag]=True
            if oldreport.get('issues'):report['resolvedHistoricalIssues']=dict(report=ref(oldpath),resolution='Approved southwest-grout repair and approved current963d beam-wall details; exact evidence is attached per image.')
            out[tile/'qa'/name]=report
        expected=31 if tile==T else 35
        assert len(merged)==expected,(tile.name,len(merged))
        out[tile/'qa/final-local-review.json']=dict(reviewedAt=now(),candidate=candidate_ref,items=list(merged.values()),sourceMigration=ref(F/'application.json'),status='current_visual_reports_merged_pending_root_finalizer',scopedLocalSeamsPassed=False,allCurrentQAReportsMerged=True,rootFinalizerApprovalPending=True,issueCount=0,issues=[],formalAccepted=False,navigationVerified=False,clientVerified=False,acceptanceNote='Current visual evidence merged; this is not the generic finalizer approval.')
        summary.append(dict(tile=tile.name,candidate=candidate_ref,mergedImageCount=len(merged)))
    # Immutable source assembly files were copied into TEXT history before applying.
    for tile in [T,S]:
        q=tile/'output/native-assembly.json';h=history/tile.name/'output/native-assembly.json';assert sha(q)==sha(h)
    return out,dict(checkedAt=now(),tiles=summary,unchangedQAByteAndPixelEqualityCount=58,changedQAApprovedProposalCanonicalEqualityCount=7,additionalRootCurrentViewCount=3,nativeAssembliesUnchanged=True,finalizerApproveExecuted=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args()
    outputs,summary=build()
    if args.write:
        marker=F/'current-review-merge.json';assert not marker.exists(),'Single-use review merge; inspect existing record instead of blindly repeating'
        for path,data in outputs.items():write(path,data)
        for tile in [T,S]:
            p=tile/'output/manifest.json';d=read(p)
            d['scopedReviewRecord']=ref(tile/'qa/final-local-review.json');d['currentVisualReportsMerged']=True;d['rootFinalizerApprovalPending']=True;write(p,d)
        summary['writtenReports']=[ref(p) for p in outputs];write(marker,summary)
    print(json.dumps(dict(writesPerformed=args.write,**summary)))

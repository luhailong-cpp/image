"""Read-only by default. --prepare writes proposal evidence only; --apply is explicit.

Apply must wait for all 16 r09_c15 native outputs. Original requests and assembly
records remain historical. Only current plans/QA/manifest pointers migrate.
No original whole-image backup or deletion is performed.
"""
from pathlib import Path
import argparse,copy,hashlib,io,json,re,shutil,sys
from PIL import Image,ImageChops

F=Path(__file__).resolve().parent
T=F.parents[1]; ROOT=T.parent
sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
from native_assemble import full_strip

OLD='26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc'
C=T/'output/r09_c14-candidate.png'
P=F/'r09_c14-proposal.png'
S=ROOT/'r10_c14'; E=ROOT/'r09_c15'
SC=S/'output/r10_c14-candidate.png'

def ref(p):return dict(file=str(p),sha256=sha(p))
def pixels(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
def encoded(im):
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def image(p):return Image.open(p).convert('RGB')
def pnghash(im):return hashlib.sha256(encoded(im)).hexdigest()

def folded(band,vertical=False):
    out=Image.new('RGB',(1024,1280))
    for i in range(4):
        p=band.crop((0,1024*i,320,1024*(i+1))) if vertical else band.crop((1024*i,0,1024*(i+1),320))
        if vertical:p=p.transpose(Image.Transpose.ROTATE_90)
        out.paste(p,(0,320*i))
    return out

def reproduce(path,im,neighbors):
    """Reproduce each retained native QA image from its recorded scale-1 scope."""
    name=path.stem;d=read(str(path)+'.generation.json');op=d['operation']
    if name.startswith('internal-') or name in ['north-return-256-full','west-return-256-full']:
        return full_strip(im,op['axis'],op['position'])[0]
    if name.startswith('junction-'):return im.crop(op['cropLTRB'])
    if name=='west-shared-full':
        band=Image.new('RGB',(320,4096));band.paste(neighbors['west'].crop((3936,0,4096,4096)),(0,0));band.paste(im.crop((0,0,160,4096)),(160,0));return folded(band,True)
    if name=='north-shared-full':
        band=Image.new('RGB',(4096,320));band.paste(neighbors['north'].crop((0,3936,4096,4096)),(0,0));band.paste(im.crop((0,0,4096,160)),(0,160));return folded(band)
    if name.endswith('-no-neighbor-unverified'):
        return folded(im.crop(op['cropLTRB']),name.startswith('east'))
    if name.startswith('west-segment-'):
        out=Image.new('RGB',(512,1024));out.paste(neighbors['west'].crop(op['oldSourceBoxLTRB']),(0,0));out.paste(im.crop(op['candidateSourceBoxLTRB']),(256,0));return out
    if name.startswith('west-unrotated-') or name=='west-beam-attachment-native':
        out=Image.new('RGB',Image.open(path).size);out.paste(neighbors['west'].crop(op['neighborCropLTRB']),(0,0));out.paste(im.crop(op['candidateCropLTRB']),(op['seamX'],0));return out
    if 'four-tile-corner' in name:
        size=Image.open(path).width;h=size//2;out=Image.new('RGB',(size,size))
        out.paste(neighbors['northwest'].crop((4096-h,4096-h,4096,4096)),(0,0));out.paste(neighbors['north'].crop((0,4096-h,h,4096)),(h,0));out.paste(neighbors['west'].crop((4096-h,0,4096,h)),(0,h));out.paste(im.crop((0,0,h,h)),(h,h));return out
    raise ValueError('No verified QA recipe: '+str(path))

def qa_paths(tile):
    paths=list((tile/'qa/native-candidate').glob('*.png'))+list((tile/'qa/external-details').glob('*.png'))
    for n in ['north-no-neighbor-unverified.png','four-tile-corner.png']:
        p=tile/'qa'/n
        if p.exists():paths.append(p)
    return sorted(paths)

def build(export=False):
    assert sha(C)==OLD,'Current old north must remain unchanged until explicit application'
    assert sha(P)==read(F/'proposal-index.json')['proposalTile']['sha256']
    before=image(C);after=image(P);diff=ImageChops.difference(before,after)
    assert list(diff.getbbox())==[0,3908,257,4096]
    rightbox=(3981,0,4096,4096)
    assert before.crop(rightbox).tobytes()==after.crop(rightbox).tobytes()
    # Pin current south candidate before constructing evidence; no asynchronous file mutation tolerated.
    south_ref=ref(SC);south=image(SC)
    nplan=read(T/'plan.json');splan=read(S/'plan.json')
    west=image(Path(nplan['westCandidate']))
    southneighbors={k:image(Path(splan[n])) for k,n in [('north','northCandidate'),('west','westCandidate'),('northwest','northWestCandidate')]}
    rows=[]
    for tile,oldim,newim,oldn,newn in [(T,before,after,{'west':west},{'west':west}),(S,south,south,southneighbors,dict(southneighbors,north=after))]:
        for path in qa_paths(tile):
            oldqa=reproduce(path,oldim,oldn);newqa=reproduce(path,newim,newn);current=image(path)
            assert oldqa.size==current.size and oldqa.tobytes()==current.tobytes(), 'Current QA not reproduced: '+str(path)
            same=oldqa.tobytes()==newqa.tobytes()
            rec=dict(tile=tile.name,canonical=str(path),currentFileSha256=sha(path),currentPixelSha256=pixels(current),reproducedCurrentPngSha256=pnghash(oldqa),reproducedCurrentPixelSha256=pixels(oldqa),currentByteReproduced=sha(path)==pnghash(oldqa),currentPixelsReproduced=True,newPngSha256=pnghash(newqa),newPixelSha256=pixels(newqa),changed=not same,exactPixelReuse=same,exactByteReuse=same and sha(path)==pnghash(newqa),newVisualInspectionClaimed=False,pixels=list(newqa.size),operation=read(str(path)+'.generation.json')['operation'])
            if not same:
                out=F/'qa-proposed'/tile.name/path.relative_to(tile/'qa')
                rec['proposalQA']=str(out)
                if export:
                    out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(encoded(newqa))
                    write(str(out)+'.generation.json',dict(file=str(out),sha256=sha(out),createdAt=now(),nativeScale=1,actuallyViewed=False,operation=rec['operation'],derivedFrom=[ref(P),south_ref] if tile==S else [ref(P),ref(Path(nplan['westCandidate']))],purpose='proposed dependency migration QA only; current canonical not modified'))
            rows.append(rec)
    assert sha(SC)==south_ref['sha256'],'South candidate changed during preparation'
    result=dict(checkedAt=now(),currentNorth=ref(C),proposedNorth=ref(P),currentSouth=south_ref,actualChangedTileLTRB=[0,3908,257,4096],right115=dict(cropLTRB=list(rightbox),beforePixelSha256=pixels(before.crop(rightbox)),afterPixelSha256=pixels(after.crop(rightbox)),pixelIdentical=True),south320=dict(cropLTRB=[0,3776,4096,4096],beforePixelSha256=pixels(before.crop((0,3776,4096,4096))),afterPixelSha256=pixels(after.crop((0,3776,4096,4096)))),qa=rows,currentQAReproductionCount=len(rows),changedQA=[r['canonical'] for r in rows if r['changed']],unchangedQACount=sum(not r['changed'] for r in rows),allCurrentQAPixelsReproduced=True,allCurrentQABytesReproduced=all(r['currentByteReproduced'] for r in rows),historicalRequestsMustNotBeRewritten=True,canonicalModified=False,applyRequiresAll16EastNative=True,oldWholeImageBackupCreated=False)
    if export:
        write(F/'migration-plan.json',result)
        # Native south pixels in ordinary orientation, not only the folded strip.
        p=F/'qa-proposed/r09_c14/south-first1024.png';p.parent.mkdir(parents=True,exist_ok=True);after.crop((0,3776,1024,4096)).save(p)
        write(str(p)+'.generation.json',dict(file=str(p),sha256=sha(p),nativeScale=1,actuallyViewed=False,operation=dict(cropLTRB=[0,3776,1024,4096],resampling=False),derivedFrom=[ref(P)]))
    return result

def snapshot_text(path,history,records):
    if not path.exists():return
    dest=history/path.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
    records.append(dict(originalFile=str(path),historicalRecordFile=str(dest),historicalRecordSha256=sha(dest)))

def migrate_current_ref(obj,old,new):
    """Current QA sidecars only. Never use on generation requests or historical assembly."""
    if isinstance(obj,dict):
        if obj.get('file')==str(C) and obj.get('sha256')==old:obj['sha256']=new
        for value in obj.values():migrate_current_ref(value,old,new)
    elif isinstance(obj,list):
        for value in obj:migrate_current_ref(value,old,new)

def apply():
    plan=build(False);saved=read(F/'migration-plan.json')
    assert plan['currentSouth']==saved['currentSouth'] and plan['changedQA']==saved['changedQA'],'Prepared QA is stale; run --prepare and inspect changed views again'
    assert len(plan['qa'])==len(saved['qa'])
    assert [r['canonical'] for r in plan['qa']]==[r['canonical'] for r in saved['qa']]
    for a,b in zip(plan['qa'],saved['qa']):assert a['newPngSha256']==b['newPngSha256'] and a['currentFileSha256']==b['currentFileSha256']
    review=read(F/'migration-qa-review.json')
    assert review['proposedNorthSha256']==sha(P) and review['southCandidateSha256']==sha(SC)
    inspected={v['sha256']:v for v in review['items'] if v.get('actuallyViewed') is True and type(v.get('nativeScale')) in [int,float] and v['nativeScale']==1 and v.get('verdict') in ['pass','scoped_pass']}
    assert all(r['newPngSha256'] in inspected for r in plan['qa'] if r['changed']),'Every changed QA needs actual review'
    authorization=read(F/'root-migration-authorization.json')
    assert authorization['applyAuthorized'] is True and authorization['proposedNorthSha256']==sha(P) and authorization['currentSouthSha256']==sha(SC)
    assert authorization['all16EastNativeComplete'] is True
    # This is an internal scheduling guard; no mutation during r09_c15 generation.
    for row in range(1,5):
        for col in range(1,5):
            p=E/f'native/p{row}{col}.png';g=read(str(p)+'.generation.json');assert sha(p)==g['sha256']
    ep=read(E/'plan.json');assert ep['westCandidateSha256']==OLD
    assert read(S/'plan.json')['northCandidateSha256']==OLD
    history=F/'history-before-application';assert not history.exists(),'Single-use apply; inspect recovery journal rather than repeat'
    history.mkdir();hist=[]
    # Text only; preserve all affected mutable review/source declarations before overwrite.
    paths=set()
    for tile in [T,S]:
        paths.update((tile/'qa').rglob('*.json'))
        paths.update([tile/'plan.json',tile/'output/manifest.json',tile/'output/native-assembly.json',tile/'output'/f'{tile.name}-candidate.png.generation.json'])
    paths.update([S/'preparation.json',E/'plan.json',E/'preparation.json',E/'output/manifest.json'])
    paths.update(tile/'progress.json' for tile in [T,S,E])
    for p in sorted(paths):snapshot_text(p,history,hist)
    newsha=sha(P);application=F/'application.json'
    record=dict(startedAt=now(),status='prepared_text_history_complete',canonical=str(C),oldImageSha256=OLD,newImageSha256=newsha,oldImageStatus='retired_after_application_no_backup_copy',textHistory=hist,proof=ref(F/'migration-plan.json'),visualReview=ref(F/'migration-qa-review.json'),rootAuthorization=ref(F/'root-migration-authorization.json'),oldWholeImageBackupCreated=False,formalAccepted=False)
    write(application,record)
    shutil.copyfile(P,C);assert sha(C)==newsha
    for r in saved['qa']:
        p=Path(r['canonical'])
        if r['changed']:
            q=Path(r['proposalQA']);assert sha(q)==r['newPngSha256'];shutil.copyfile(q,p)
        assert sha(p)==r['newPngSha256']
        side=Path(str(p)+'.generation.json');d=read(side);migrate_current_ref(d,OLD,newsha);d.update(sha256=sha(p),currentNorthSourceSha256=newsha,migrationRecord=str(application))
        d['reviewProvenance']=dict(changed=r['changed'],previousQAImageSha256=r['currentFileSha256'],newQAImageSha256=sha(p),exactPixelReuse=r['exactPixelReuse'],newVisualInspectionClaimed=False,proposalVisualReview=str(F/'migration-qa-review.json') if r['changed'] else None)
        write(side,d)
    # Frozen planning inputs and actual AI request evidence stay untouched; current scoped crop gets a new filename.
    crop=S/'references/north-native320-after-grout.png';image(C).crop((0,3776,4096,4096)).save(crop)
    write(str(crop)+'.generation.json',dict(file=str(crop),sha256=sha(crop),derivedFrom=[ref(C)],operation=dict(kind='unchanged-scale current north scope after approved repair',cropLTRB=[0,3776,4096,4096],resampling=False),productionPixels=False))
    for path in [S/'plan.json',S/'preparation.json']:
        if not path.exists():continue
        d=read(path)
        if 'northCandidateSha256' in d:d['northCandidateSha256']=newsha
        if isinstance(d.get('north'),dict):d['north']['sha256']=newsha
        scope=d.get('northScopedFreeze',{})
        scope.update(file=str(crop),sha256=sha(crop),pixelSha256=pixels(image(crop)),sourceFile=str(C),sourceFileSha256AtFreeze=newsha,sourceCropLTRB=[0,3776,4096,4096],wholeSourceStillUnderQA=False,laterWholeSourceRevalidationRequired=False,revalidatedCurrentWholeSourceSha256=newsha,revalidatedAt=now(),revalidationRecord=str(application),historicalPreviousFreezeInTextHistory=True)
        d['northScopedFreeze']=scope;d['currentNorthMigration']=str(application);write(path,d)
    ep['westCandidateSha256']=newsha;ep['westSourceMigration']=dict(record=str(application),actualSubmittedSourceSha256=OLD,currentWholeSourceSha256=newsha,right115PixelsUnchanged=True);write(E/'plan.json',ep)
    prep=E/'preparation.json'
    if prep.exists():
        d=read(prep)
        for key in ['west','westCandidate']:
            if isinstance(d.get(key),dict) and d[key].get('sha256')==OLD:d[key]['sha256']=newsha
        if d.get('westCandidateSha256')==OLD:d['westCandidateSha256']=newsha
        d['currentWestMigration']=str(application);write(prep,d)
    record.update(appliedAt=now(),status='applied_pending_root_current_QA_finalization',currentNorth=ref(C),currentSouth=ref(SC),right115PixelsUnchanged=True,nativeRequestsRewritten=False,canonicalSouthPixelsChanged=False)
    write(application,record)
    oldgen=history/'r09_c14/output/r09_c14-candidate.png.generation.json'
    write(str(C)+'.generation.json',dict(file=str(C),sha256=newsha,createdAt=now(),width=4096,height=4096,format='PNG',derivedFrom=[dict(file=str(C),sha256=OLD,historical=True,retired=True,fileNoLongerContainsTheseBytes=True,generationRecord=str(oldgen)),ref(P)],operation=ref(application),submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,productionPixels=True,formalAccepted=False,clientVerified=False,navigationVerified=False))
    # Keep historical native assembly immutable. Current manifests/reviews require explicit root finalization.
    for tile in [T,S,E]:
        p=tile/'output/manifest.json'
        if not p.exists():continue
        d=read(p)
        # Patch acquisition/repair history stays as originally recorded.
        for key in ['neighbors','currentNeighbors']:
            for r in d.get(key,{}).values():
                if r.get('file')==str(C) and r.get('sha256')==OLD:r['sha256']=newsha
        for r in d.get('qa',[]):
            q=Path(r['file'])
            if q.exists():r['sha256']=sha(q)
            migrate_current_ref(r,OLD,newsha)
        if tile==T:d['sha256']=newsha;d['currentCandidateGeneration']=ref(Path(str(C)+'.generation.json'))
        d.update(status='current_source_migration_pending_root_finalization',scopedLocalSeamsPassed=False,sourceMigration=str(application),formalAccepted=False)
        if tile==T:d['historicalNativeAssemblyUnchanged']=True
        write(p,d)
    index=T/'qa/native-candidate/current-index.json';d=read(index);migrate_current_ref(d,OLD,newsha);d['candidate']=ref(C)
    for key in ['standardQA','unrotatedWestDetails']:
        for r in d.get(key,[]):r['sha256']=sha(r['file'])
    d['currentSourceMigration']=str(application);d['allCurrentImagesPendingVisualReview']=False;d['finalRootReviewPending']=True;write(index,d)
    index=S/'qa/external-details/index.json'
    if index.exists():
        d=read(index);migrate_current_ref(d.get('sources',{}),OLD,newsha);d['candidate']=ref(SC)
        for r in d.get('records',[]):
            q=Path(r['file']);r['sha256']=sha(q)
            migrate_current_ref(r.get('sources',{}),OLD,newsha)
        d['currentSourceMigration']=str(application);d['finalRootReviewPending']=True;write(index,d)
    for tile in [T,S]:
        for name in ['final-local-review.json','external-review.json']:
            p=tile/'qa'/name
            if not p.exists():continue
            d=read(p);d.update(status='historical_reviews_preserved_pending_migration_merge',sourceMigration=str(application),currentCandidate=ref(C if tile==T else SC),finalRootReviewPending=True,formalAccepted=False)
            d['scopedLocalSeamsPassed']=False;d['externalScopedPass']=False
            d['historicalReviewItems']=True
            d['historicalReviewSnapshot']=str(history/p.relative_to(ROOT))
            # Existing item claims describe their historical hashes and are deliberately not rewritten.
            write(p,d)
    for tile in [T,S,E]:
        p=tile/'progress.json'
        if not p.exists():continue
        d=read(p);d.update(updatedAt=now(),stage='current_source_migration_pending_root_finalization',scopedLocalSeamsPassed=False,sourceMigration=str(application),formalAccepted=False)
        candidate=tile/'output'/f'{tile.name}-candidate.png'
        if candidate.exists():d.update(file=str(candidate),sha256=sha(candidate))
        if tile==E:d['currentWestCandidate']=ref(C)
        else:d['currentCandidate']=ref(candidate)
        d['historicalProgressSnapshot']=str(history/p.relative_to(ROOT));write(p,d)
    for tile in [T,S]:
        p=tile/'output/manifest.json'
        if p.exists():
            d=read(p)
            if isinstance(d.get('scopedReviewRecord'),dict):
                q=Path(d['scopedReviewRecord']['file'])
                if q.exists():d['scopedReviewRecord']['sha256']=sha(q)
            write(p,d)
    assert sha(C)==newsha and sha(SC)==saved['currentSouth']['sha256']
    print(json.dumps(dict(applied=True,currentNorth=ref(C),application=str(application),rootFinalizationPending=True)))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--prepare',action='store_true');g.add_argument('--apply',action='store_true');args=p.parse_args()
    if args.apply:apply()
    else:
        r=build(args.prepare);print(json.dumps(dict(readOnly=not args.prepare,canonicalModified=False,total=r['currentQAReproductionCount'],changed=r['changedQA'],unchanged=r['unchangedQACount'],allCurrentQABytesReproduced=r['allCurrentQABytesReproduced'],right115Unchanged=r['right115']['pixelIdentical'],currentSouth=r['currentSouth'],proposedNorth=r['proposedNorth']),ensure_ascii=False))

"""Prepare and verify r10_c13 retirement; deletions run only in scoped PowerShell."""
from pathlib import Path
import hashlib,json,datetime,sys
from PIL import Image
T=Path(__file__).resolve().parent.parent
ASSETS={'.png','.jpg','.jpeg','.webp','.gif','.tif','.tiff','.bmp','.npy','.npz'}
EXPECTED='c6c7176ea72228aca772c78a17fe8e3b5fc699904f46205d62ae482f420d1a5b'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def row(p,reason):
    p=Path(p).resolve();assert p.is_relative_to(T.resolve()) and p.is_file()
    return dict(file=str(p),sha256=sha(p),bytes=p.stat().st_size,reason=reason)

def prepare():
    manifest=read(T/'output/manifest.json'); final=read(T/'qa/final-local-review.json')
    assert manifest['scopedLocalSeamsPassed'] and final['all27StandardQAImagesActuallyViewed'] and final['additionalFourTileCornerPassed']
    assert manifest['sha256']==EXPECTED==sha(manifest['file'])
    with Image.open(manifest['file']) as im:assert im.size==(4096,4096)
    keep={}
    def add(p,reason):
        q=row(p,reason);keep[q['file'].lower()]=q
    add(manifest['file'],'final exported native 4096 candidate; runtime dependency')
    for p in manifest['patches']:
        for x in p['fields'].values():
            assert sha(x['file'])==x['sha256'];add(x['file'],'applied registration field/mask')
    qa=manifest['qaImages'] if 'qaImages' in manifest else manifest['qa']
    assert len(qa)==27
    for x in qa:
        assert x['actuallyViewed'] and sha(x['file'])==x['sha256'];add(x['file'],'final current native QA; east/south actual pixels only, neighbor unverified')
    corner=[x for x in final['rootItems'] if Path(x['file']).name=='four-tile-corner.png']
    assert len(corner)==1 and corner[0]['verdict']=='scoped_pass'
    add(corner[0]['file'],'passed four-tile corner QA')
    external=read(T/'qa/external-review.json')
    assert len(external['supplementalQA'])==4
    for x in external['supplementalQA']:
        assert x['actuallyViewed'] and x['verdict']=='pass' and sha(x['file'])==x['sha256'];add(x['file'],'passed external west seam supplemental QA')
    for name in ('shared-structure-aligned.png','structure-aligned.png'):add(T/'references'/name,'current common/night structure design')
    assert len(keep)==99
    retired=[row(p,'exported intermediate/rejected/old planning/old QA/unused field') for p in sorted(T.rglob('*')) if p.is_file() and p.suffix.lower() in ASSETS and str(p.resolve()).lower() not in keep]
    text=[row(p,'preserve all text evidence and integration documents') for p in sorted(T.rglob('*')) if p.is_file() and p.suffix.lower() not in ASSETS and p.name not in ('retention-plan.json','retention-log.json')]
    out=dict(createdAt=now(),mode='authorized_execute_after_scope_and_hash_preflight',scopeDirectory=str(T.resolve()),candidate=row(manifest['file'],'protected final'),finalManifest=row(T/'output/manifest.json','final manifest before retention annotation'),finalReview=row(T/'qa/final-local-review.json','completed QA'),readyToExecute=True,authorization='Root delegated user retention preference execution after final manifest completion.',retained=list(keep.values()),deleteAfterGates=retired,preservedTextInventory=text,preserveAllTextFiles=True,pendingQA=[],counts=dict(retained=len(keep),deleteAfterGates=len(retired),deleteBytes=sum(x['bytes'] for x in retired),preservedText=len(text)),deletionPerformed=False)
    write(T/'retention-plan.json',out)
    print(json.dumps(out['counts']))

def finalize():
    plan=read(T/'retention-plan.json');log=read(T/'retention-log.json')
    assert log['deletionPerformed'] and len(log['deleted'])==len(plan['deleteAfterGates'])
    assert sha(plan['candidate']['file'])==EXPECTED
    deleted={str(Path(x['file']).resolve()).lower():x for x in log['deleted']}
    for x in plan['deleteAfterGates']:assert not Path(x['file']).exists()
    for x in plan['retained']:assert Path(x['file']).is_file() and sha(x['file'])==x['sha256']
    for x in plan['preservedTextInventory']:assert Path(x['file']).is_file() and sha(x['file'])==x['sha256']
    note=dict(completedAt=now(),policy='User 2026-09-23 final-assets-only retention',log=str(T/'retention-log.json'),plan=str(T/'retention-plan.json'),sourceRecordsHistorical=True,sourceImagePathsRetired=True,historicalReferenceMeaning='Historical source image paths retain original hashes and provenance, but retired intermediate image files are intentionally absent after verified 4096 export. They are not runtime dependencies.',runtimeDependencies=plan['candidate'],keptAssets=plan['counts']['retained'],deletedAssets=len(deleted),deletedBytes=plan['counts']['deleteBytes'])
    manifest_path=T/'output/manifest.json';manifest=read(manifest_path);manifest['retention']=note
    for p in manifest['patches']:
        if str(Path(p['source']['file']).resolve()).lower() in deleted:
            p['source']['retiredAfterExport']=True;p['source']['runtimeDependency']=False
    write(manifest_path,manifest)
    generation_path=Path(str(plan['candidate']['file'])+'.generation.json');g=read(generation_path);g['retention']=note
    for s in g.get('derivedFrom',[]):
        if str(Path(s['file']).resolve()).lower() in deleted:s['retiredAfterExport']=True;s['runtimeDependency']=False
    write(generation_path,g)
    errors=[];current=[];historical=[]
    def walk(v,record,key='$'):
        if isinstance(v,dict):
            if isinstance(v.get('file'),str) and isinstance(v.get('sha256'),str) and Path(v['file']).is_absolute():
                p=Path(v['file']); k=str(p.resolve()).lower();check=dict(file=str(p),expectedSha256=v['sha256'],record=record,field=key)
                if k in deleted:check['classification']='intentionally_retired_historical_source';historical.append(check)
                elif p.is_file() and sha(p)==v['sha256']:check['passed']=True;current.append(check)
                else:check['actualSha256']=sha(p) if p.is_file() else None;errors.append(check)
            for k,x in v.items():walk(x,record,key+'.'+k)
        elif isinstance(v,list):
            for i,x in enumerate(v):walk(x,record,key+f'[{i}]')
    for p in (manifest_path,generation_path,T/'qa/final-local-review.json',T/'qa/external-review.json',T/'qa/horizontal-review.json'):
        walk(read(p),str(p))
    # Current design derivative source pointers are historical; their selected file hashes remain live.
    for name in ('shared-structure-aligned.png','structure-aligned.png'):
        p=T/'references'/(name+'.generation.json');walk(read(p),str(p))
    remaining=[str(p.resolve()).lower() for p in T.rglob('*') if p.is_file() and p.suffix.lower() in ASSETS]
    assert set(remaining)=={x['file'].lower() for x in plan['retained']}
    audit=dict(auditedAt=now(),candidate=dict(file=plan['candidate']['file'],sha256=sha(plan['candidate']['file']),pixels=[4096,4096]),retainedAssetsVerified=len(remaining),preservedTextBeforeAnnotation=len(plan['preservedTextInventory']),annotationChangedOnly=[str(manifest_path),str(generation_path)],currentReferenceCount=len(current),historicalReferenceCount=len(historical),unexpectedErrorCount=len(errors),errors=errors,currentReferences=current,intentionallyRetiredHistoricalReferences=historical,formalAccepted=False,clientVerified=False,navigationVerified=False)
    write(T/'evidence/post-retention-audit.json',audit)
    assert not errors,errors
    log['postRetirementAudit']=str(T/'evidence/post-retention-audit.json');log['candidateHashAfter']=sha(plan['candidate']['file']);log['retainedAssetCountVerified']=len(remaining);log['completedAt']=now();write(T/'retention-log.json',log)
    print(json.dumps({k:audit[k] for k in ['retainedAssetsVerified','preservedTextBeforeAnnotation','currentReferenceCount','historicalReferenceCount','unexpectedErrorCount']}))

if __name__=='__main__':
    {'prepare':prepare,'finalize':finalize}[sys.argv[1]]()

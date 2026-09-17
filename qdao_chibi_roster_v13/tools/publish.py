"""Explicit, transactional V13 staging/publication. Default: read-only dry run."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, shutil, sys, uuid
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'candidate/24_lu_dongbin'
WORK=Path('E:/work').resolve()
FORMAL=(WORK/'mmorpg-client').resolve()
RESOURCE=Path('Assets/Resources/World/Characters/QdaoRosterV13/24_lu_dongbin')
CHARACTER='24_lu_dongbin'
NAMESPACE=uuid.UUID('314b9c25-aac8-4e09-9b8f-b8f3ae52d51f')
FOLDER_META='fileFormatVersion: 2\nguid: {guid}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n'
TEXT_META='fileFormatVersion: 2\nguid: {guid}\nTextScriptImporter:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n'

def require(ok,message):
    if not ok: raise ValueError(message)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
def time_utc(value):
    parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
def inside(path,parent=WORK):
    absolute=Path(os.path.abspath(path))
    for ancestor in (absolute,*absolute.parents):
        require(not ancestor.is_symlink() and not (hasattr(ancestor,'is_junction') and ancestor.is_junction()),f'Refusing symlink/junction ancestor: {ancestor}')
    resolved=absolute.resolve();require(resolved.is_relative_to(Path(parent).resolve()),f'Path escapes allowed root: {path}');return resolved
def no_links(path):
    path=Path(path)
    for p in [path,*path.rglob('*')] if path.exists() else []:
        require(not p.is_symlink() and not (hasattr(p,'is_junction') and p.is_junction()),f'Refusing symlink/junction in transaction input: {p}')
def inventory(path):
    no_links(path)
    return [{'path':p.relative_to(path).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(Path(path).rglob('*')) if p.is_file()]
def candidate():
    spec=importlib.util.spec_from_file_location('v13_publication_verify',ROOT/'tools/verify.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    # Independent recomputation does not rewrite the signed validation timestamp.
    fresh=verifier.verify(require_visual=True)
    recorded=read(SOURCE/'validation.json')
    require(read(SOURCE/'manifest.json').get('status')=='passed' and read(SOURCE/'qc.json').get('status')=='passed' and read(SOURCE/'qc.json').get('visual_review')=='passed','Run tools/approve.py so final manifest, QC and visual approval states agree')
    require(recorded.get('status')=='passed','Run tools/verify.py --require-visual after final candidate review')
    require({k:v for k,v in recorded.items() if k!='verified_at_utc'}=={k:v for k,v in fresh.items() if k!='verified_at_utc'},'Recorded validation differs from independent re-verification')
    approvals={f'{name}_sha256':sha(SOURCE/f'{name}.json') for name in ('manifest','qc','validation')}
    require(recorded['manifest_sha256']==approvals['manifest_sha256'] and recorded['qc_sha256']==approvals['qc_sha256'],'Validation references stale manifest or QC')
    revision=hashlib.sha256(json.dumps(approvals,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    artifacts=fresh['artifacts'];require(len(artifacts)==145,'Expected 145 delivery PNGs')
    return approvals,revision,artifacts

def project_path(value):
    p=inside(value);require((p/'Assets').is_dir() and (p/'ProjectSettings/ProjectVersion.txt').is_file(),f'Not an existing Unity project: {p}')
    target=inside(p/RESOURCE,p);require(target.relative_to(p).as_posix()==RESOURCE.as_posix(),'V13 resource path resolves to a different directory');return p

def checked_evidence(record,approval_dir):
    path=Path(record['path']);path=path if path.is_absolute() else approval_dir/path
    path=inside(path)
    require(path.is_file() and sha(path)==record['sha256'],f'Runtime evidence missing or changed: {path}')
    return path

def pending_v13(relative):
    return relative.startswith(RESOURCE.as_posix()+'/') or relative in (RESOURCE.as_posix()+'.meta',RESOURCE.parent.as_posix()+'.meta')
def relevant_input(relative):
    if pending_v13(relative):return False
    exact={'Assets/Scripts/World/ActorWorld.cs','Assets/Scripts/Game/GameClient.cs','Assets/Scripts/World/Tianyong/TianyongPlayerController.cs','Assets/Scripts/World/Tianyong/TianyongSandboxBootstrap.cs','Assets/Scripts/UI/Ugui/Battle/BattleArtCatalog.cs'}
    bare=relative.removesuffix('.meta')
    return bare in exact or relative.startswith(('Assets/Scripts/World/Qdao','Assets/Editor/Qdao','Assets/Resources/World/Characters/QdaoRoster','Packages/','ProjectSettings/')) or relative.endswith(('.asmdef','.asmref','.asmdef.meta','.asmref.meta')) or relative.startswith('Assets/Tests/') and ('Qdao' in Path(relative).name or 'BattleRosterAppearance' in Path(relative).name)
def runtime_approval(path,revision,approvals,artifacts,publish_project):
    p=inside(path);a=read(p);parent=p.parent
    require(a.get('schema')=='qdao-v13-runtime-approval/v1' and a.get('status')=='passed','Wrong/unpassed V13 runtime approval')
    require(a.get('candidateRevision')==revision and a.get('sourceApprovals')==approvals,'Runtime approval is for another candidate revision')
    require(a.get('characterId')==CHARACTER and a.get('version')==13,'Runtime approval does not cover V13 Lu Dongbin')
    receipt_path=checked_evidence(a['stagingReceipt'],parent);receipt=read(receipt_path)
    require(receipt.get('status')=='passed' and receipt.get('mode')=='stage' and receipt.get('candidateRevision')==revision,'Runtime input receipt is not this candidate staging')
    tested=project_path(receipt['clientProject']);require(tested!=FORMAL,'Runtime approval must come from an isolated project')
    require(receipt.get('sourceApprovals')==approvals,'Staged approval hashes do not match current candidate')
    actual={f['path']:f['sha256'] for f in artifacts};require(receipt.get('pngFiles')==actual,'Staging receipt has different PNG assets')
    # Verify that the saved tested resources still represent the same input snapshot.
    for relative,digest in actual.items():require(sha(tested/RESOURCE/relative)==digest,f'Runtime snapshot asset changed: {relative}')
    require(sha(tested/RESOURCE/'appearance.json')==receipt['appearanceSha256'],'Runtime snapshot activation changed')
    snapshot_path=checked_evidence(a['inputSnapshot'],parent);snapshot=read(snapshot_path)
    require(project_path(snapshot['project'])==tested,'Input snapshot belongs to another validation project')
    require(snapshot.get('shared_writable_links') is False,'Runtime snapshot does not attest to isolated storage')
    rows=snapshot.get('files',[]);indexed={r['path']:r for r in rows}
    require(len(indexed)==len(rows) and snapshot.get('count')==len(rows),'Input snapshot file inventory is malformed')
    critical={'Assets/Scripts/World/QdaoCharacterCatalog.cs','Assets/Scripts/World/QdaoBoySpriteAnimator.cs','Assets/Editor/QdaoCharacterSpriteImporter.cs','Assets/Editor/QdaoFrameAlphaProcessor.cs','Assets/Tests/EditMode/Tianyong/QdaoAppearanceVersionTests.cs','Assets/Tests/PlayMode/QdaoRosterSandboxPlayModeTests.cs','ProjectSettings/ProjectVersion.txt','Packages/manifest.json','Assets/Scripts/World/ActorWorld.cs','Assets/Scripts/Game/GameClient.cs','Assets/Scripts/World/Tianyong/TianyongPlayerController.cs','Assets/Scripts/World/Tianyong/TianyongSandboxBootstrap.cs','Assets/Scripts/UI/Ugui/Battle/BattleArtCatalog.cs'}
    require(critical.issubset(indexed),'Input snapshot lacks the core runtime, importer, tests, or Unity configuration')
    saved_files=set()
    for folder in ('Assets','Packages','ProjectSettings'):
        no_links(tested/folder)
        saved_files.update(p.relative_to(tested).as_posix() for p in (tested/folder).rglob('*') if p.is_file())
    require(saved_files==set(indexed),'Saved isolated project file set differs from tested input snapshot')
    target_files={p.relative_to(publish_project).as_posix() for folder in ('Assets','Packages','ProjectSettings') for p in (publish_project/folder).rglob('*') if p.is_file()}
    require({p for p in target_files if relevant_input(p)}=={p for p in indexed if relevant_input(p)},'Publication project relevant code/resource/configuration file set differs from tested snapshot')
    unrelated_differences=[]
    for relative,row in indexed.items():
        require(relative.split('/')[0] in ('Assets','Packages','ProjectSettings'),'Input snapshot contains an unexpected root')
        saved=inside(tested/relative,tested)
        require(saved.is_file() and sha(saved)==row['sha256'] and saved.stat().st_size==row['bytes'],f'Tested input changed after snapshot: {relative}')
        if not pending_v13(relative):
            destination=inside(publish_project/relative,publish_project);digest=sha(destination) if destination.is_file() else None
            if relevant_input(relative):require(digest==row['sha256'],f'Publication project relevant input differs from tested snapshot: {relative}')
            elif digest!=row['sha256']:unrelated_differences.append({'path':relative,'testedSha256':row['sha256'],'currentSha256':digest})
    for relative in sorted(target_files-set(indexed)):
        if not pending_v13(relative) and not relevant_input(relative):unrelated_differences.append({'path':relative,'testedSha256':None,'currentSha256':sha(inside(publish_project/relative,publish_project))})
    for relative,digest in actual.items():
        resource_path=(RESOURCE/relative).as_posix()
        require(resource_path in indexed and indexed[resource_path]['sha256']==digest,f'Tested input snapshot does not contain this V13 PNG: {relative}')
    appearance_path=(RESOURCE/'appearance.json').as_posix()
    require(appearance_path in indexed and indexed[appearance_path]['sha256']==receipt['appearanceSha256'],'Tested input snapshot lacks this exact V13 activation')
    snapshot_time=time_utc(snapshot['created_utc'])
    require(snapshot_time>=time_utc(receipt['createdAtUtc']),'Test input snapshot predates candidate staging')
    observed=read(checked_evidence(a['runtimeObservation'],parent))
    require(observed.get('schemaVersion')==1 and observed.get('behaviorAssertionsCompleted') is True,'Unity runtime behavior assertions did not complete')
    require(observed.get('inputSnapshotSha256')==sha(snapshot_path) and project_path(observed['projectPath'])==tested,'Runtime observation belongs to another tested input/project')
    actors=observed.get('appearances',[]); by_id={item.get('requestedCharacterId'):item for item in actors}
    expected_ids={'23_lantern_courier','24_lu_dongbin','25_lion_drum_guard','26_osmanthus_healer','27_ink_kite_ranger','28_moon_rabbit_artificer','29_he_xiangu','30_han_xiangzi'}
    require(len(actors)==8 and set(by_id)==expected_ids,'Unity observation must include all eight roster identities')
    directions=('N','NE','E','SE','S','SW','W','NW')
    for identifier,item in by_id.items():
        version=13 if identifier==CHARACTER else 12; count=16 if version==13 else 8
        require(item.get('actualCharacterId')==identifier and item.get('actualArtworkVersion')==version and item.get('catalogVersion')==version,'Runtime loaded a wrong identity or appearance version')
        require(item.get('actualFrameCount')==count and item.get('actualHasDedicatedIdle') is True and item.get('actualFramesMatchResources') is True,'Actual animation inventory does not match dedicated resources')
        for field in ('actualFramesPerDirection','actualUniqueFrameSpritesPerDirection','actualUniqueFrameTexturesPerDirection'):
            require(item.get(field)=={d:count for d in directions},f'Incomplete or duplicate runtime frame inventory: {identifier}/{field}')
        require(item.get('stoppedIdle') is True and item.get('spriteMatchesDedicatedIdle') is True,'Runtime did not return to dedicated idle')
    lu=by_id[CHARACTER]
    require(lu.get('activationPresent') is True and lu.get('activationSha256')==receipt['appearanceSha256'],'Unity did not actually load this activation TextAsset')
    require(lu.get('resourceFolder')=='World/Characters/QdaoRosterV13/24_lu_dongbin' and lu.get('activationAlignmentVersion')==3 and lu.get('activationContactFrame')==0,'Runtime loaded a wrong V13 resource/alignment contract')
    require(lu.get('v13SixteenFrameContractObserved') is True and abs(lu.get('catalogFrameDurationMs',0)-30)<.001 and abs(lu.get('actualCycleDurationMs',0)-480)<.01,'Actual V13 animation timing is incorrect')
    require(lu.get('movementObserved') is True and lu.get('realMotorEnabled') is True and lu.get('actualTravelDistance',0)>0 and lu.get('actualPathDistance',0)>0 and lu.get('movementSeconds',0)>0 and lu.get('observedWalkPoseCount',0)>1,'Real controller movement was not observed')
    # Compare actual controller/animation values against the earlier genuine V12 run.
    baseline_path=checked_evidence(a['baselineRuntimeObservation'],parent); baseline=read(baseline_path)
    baseline_snapshot_path=checked_evidence(a['baselineInputSnapshot'],parent); baseline_snapshot=read(baseline_snapshot_path)
    require(baseline.get('schemaVersion')==1 and baseline.get('behaviorAssertionsCompleted') is True and baseline.get('inputSnapshotSha256')==sha(baseline_snapshot_path),'Baseline observation is not bound to a genuine V12 snapshot')
    previous=[item for item in baseline.get('appearances',[]) if item.get('requestedCharacterId')==CHARACTER]
    require(len(previous)==1,'V12 movement baseline lacks Lu Dongbin'); previous=previous[0]
    require(previous.get('actualArtworkVersion')==12 and previous.get('actualFrameCount')==8 and previous.get('movementObserved') is True and previous.get('actualFramesMatchResources') is True,'Movement baseline did not load and move genuine V12 Lu Dongbin')
    baseline_files={row['path']:row for row in baseline_snapshot.get('files',[])}
    baseline_activation='Assets/Resources/World/Characters/QdaoRosterV12/24_lu_dongbin/appearance.json'
    require(baseline_activation in baseline_files and baseline_files[baseline_activation]['sha256']==previous.get('activationSha256'),'V12 baseline activation is not in its actual input snapshot')
    for key,tolerance in (('controllerMoveSpeed',.0001),('actualCycleWorldDistance',.0001),('actualCycleDurationMs',.01)):
        require(key in lu and key in previous and abs(lu[key]-previous[key])<=tolerance,f'V13 changed actual movement/cycle value: {key}')
    require(abs(lu['actualFramesPerUnit']-2*previous['actualFramesPerUnit'])<.0001,'V13 frames per world unit did not double with frame count')
    tests=a.get('tests',[]);require({t.get('kind') for t in tests}=={'EditMode','PlayMode'} and len(tests)==2,'Both EditMode and PlayMode XML results required')
    test_summary=[]
    for t in tests:
        xml_path=checked_evidence(t,parent);tree=ET.parse(xml_path);root=tree.getroot();cases=root.findall('.//test-case')
        require(root.get('start-time') and time_utc(root.get('start-time'))>=snapshot_time,f'{t["kind"]} XML predates the V13 input snapshot')
        require(root.get('result','').lower()=='passed' and int(root.get('failed','0'))==0 and cases,f'{t["kind"]} test run did not pass')
        require(all(c.get('result','').lower()=='passed' for c in cases),f'{t["kind"]} contains failed/skipped tests')
        required=t.get('requiredV13TestNames',[]);require(required,'List the specific V13 test cases required for publication')
        passed={c.get('fullname',c.get('name')) for c in cases}
        require(all(name in passed and 'V13' in name for name in required),'Required V13 test cases absent from actual XML')
        test_summary.append({'kind':t['kind'],'passed':len(cases),'xmlSha256':sha(xml_path),'requiredV13TestNames':required})
    return {'path':str(p),'sha256':sha(p),'testedProject':str(tested),'inputSnapshotSha256':sha(snapshot_path),'tests':test_summary,'unrelatedTargetDifferences':unrelated_differences}

def meta_template(project):
    candidates=[project/'Assets/Resources/World/Characters/QdaoRosterV12/24_lu_dongbin/walk/N/01.png.meta',project/'Assets/Resources/World/Characters/QdaoHeadbandBoy/walk_N.png.meta']
    for p in candidates:
        if p.is_file():return p.read_text(encoding='utf-8')
    raise ValueError('No existing approved character TextureImporter metadata template')
def guid(path,project):return uuid.uuid5(NAMESPACE,path.relative_to(project).as_posix()).hex
def copy_meta(stage_path,final_path,project,template,kind='texture'):
    existing=Path(str(final_path)+'.meta');output=Path(str(stage_path)+'.meta')
    identifier=guid(final_path,project)
    if existing.is_file():content=existing.read_text(encoding='utf-8')
    else:content=(FOLDER_META if kind=='folder' else TEXT_META).format(guid=identifier) if kind!='texture' else re.sub(r'(?m)^guid: [0-9a-f]{32}$',f'guid: {identifier}',template)
    if kind=='texture' and final_path.name=='strip.png':content=re.sub(r'(?m)^(\s*maxTextureSize:)\s*\d+',r'\g<1> 8192',content)
    output.write_text(content,encoding='utf-8')

def execute(project,mode,approvals,revision,artifacts,runtime):
    transaction=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:10]
    evidence=inside(ROOT/'publication'/transaction,ROOT);evidence.mkdir(parents=True)
    target=inside(project/RESOURCE,project);stage=inside(project/'Temp/QdaoV13Publish'/transaction/'24_lu_dongbin',project)
    backup=inside(evidence/'before/resources',ROOT);stage.mkdir(parents=True)
    no_links(target);template=meta_template(project)
    prior=inventory(target) if target.exists() else []
    write(evidence/'before/inventory.json',{'targetExisted':target.exists(),'clientTarget':str(target),'files':prior})
    if Path(str(target)+'.meta').is_file():shutil.copy2(Path(str(target)+'.meta'),evidence/'before/character-folder.meta')
    for item in artifacts:
        src=SOURCE/item['path'];dst=inside(stage/item['path'],stage);dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst);require(sha(dst)==item['sha256'],f'Stage copy SHA mismatch: {item["path"]}')
        copy_meta(dst,target/item['path'],project,template)
    for directory in sorted((p for p in stage.rglob('*') if p.is_dir()),key=lambda p:len(p.parts)):
        copy_meta(directory,target/directory.relative_to(stage),project,template,'folder')
    # Preserve the existing activation TextAsset GUID before the old tree moves.
    copy_meta(stage/'appearance.json',target/'appearance.json',project,template,'text')
    approval={'version':13,'characterId':CHARACTER,'frameCount':16,'frameDurationMs':30,'dedicatedIdle':True,'alignmentVersion':3,'contactFrame':0,'status':'passed','visualReview':'passed',**approvals}
    # No activation exists in the staging tree. Until the final rename, the old version stays intact.
    target.parent.mkdir(parents=True,exist_ok=True)
    if not Path(str(target.parent)+'.meta').exists():copy_meta(target.parent,target.parent,project,template,'folder')
    if not Path(str(target)+'.meta').exists():copy_meta(target,target,project,template,'folder')
    require(all(sha(SOURCE/f'{name}.json')==approvals[f'{name}_sha256'] for name in ('manifest','qc','validation')),'Candidate approvals changed while staging')
    require(sha(SOURCE/'review/visual-review.json')==read(SOURCE/'validation.json')['visual_review_sha256'],'Candidate visual approval changed while staging')
    moved_old=False;moved_new=False
    try:
        if target.exists():
            backup.parent.mkdir(parents=True,exist_ok=True)
            inside(target,project);inside(backup,ROOT);os.replace(target,backup);moved_old=True
        inside(stage,project);inside(target,project);os.replace(stage,target);moved_new=True
        for item in artifacts:require(sha(target/item['path'])==item['sha256'],f'Installed PNG mismatch: {item["path"]}')
        require(not (target/'appearance.json').exists(),'Activation must remain absent until every PNG is installed')
        pending=target/'appearance.json.pending';write(pending,approval)
        os.replace(pending,target/'appearance.json')
        require(read(target/'appearance.json')==approval,'Final activation differs')
        receipt={'schema':'qdao-v13-publication-receipt/v1','status':'passed','mode':mode,'createdAtUtc':now(),'clientProject':str(project),'resourceTarget':str(target),'candidateRevision':revision,'sourceApprovals':approvals,'pngFiles':{i['path']:i['sha256'] for i in artifacts},'appearanceSha256':sha(target/'appearance.json'),'backup':str(backup) if moved_old else None,'beforeInventory':str(evidence/'before/inventory.json'),'runtimeApproval':runtime,'activationWrittenLast':True}
        write(evidence/'receipt.json',receipt)
        print(json.dumps({'status':'passed','mode':mode,'candidateRevision':revision,'pngCount':145,'receipt':str(evidence/'receipt.json'),'backup':str(backup) if moved_old else None},ensure_ascii=False))
    except Exception as error:
        # Preserve both the original and failed attempt; no recursive delete occurs.
        if moved_new and target.exists():
            displaced=inside(evidence/'failed/resources',ROOT);displaced.parent.mkdir(parents=True,exist_ok=True)
            inside(target,project);os.replace(target,displaced)
        if moved_old and backup.exists():
            inside(backup,ROOT);inside(target,project);os.replace(backup,target)
        write(evidence/'failure.json',{'status':'failed','error':str(error),'rolledBackToPriorV13':moved_old,'fallbackToV12Available':True,'time':now()})
        raise

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-project',required=True,type=Path,help='Existing Unity project strictly inside E:/work')
    parser.add_argument('--mode',required=True,choices=('stage','publish'))
    parser.add_argument('--runtime-approval',type=Path,help='Required for publish; same-candidate isolated V13 runtime approval JSON')
    parser.add_argument('--execute',action='store_true',help='Explicit opt-in to client writes. Without this flag, only verify and print the plan.')
    args=parser.parse_args();project=project_path(args.client_project)
    require(not (args.mode=='stage' and project==FORMAL),'stage is only for isolated validation copies; the formal project requires publish')
    if args.mode=='publish':require(args.runtime_approval is not None,'publish requires --runtime-approval from this exact V13 candidate')
    approvals,revision,artifacts=candidate()
    runtime=runtime_approval(args.runtime_approval,revision,approvals,artifacts,project) if args.mode=='publish' else None
    if not args.execute:
        print(json.dumps({'status':'ready_dry_run','mode':args.mode,'clientProject':str(project),'candidateRevision':revision,'sourceApprovals':approvals,'pngCount':145,'resourceTarget':str(project/RESOURCE),'runtimeApproval':runtime,'writesPerformed':False},ensure_ascii=False));return
    execute(project,args.mode,approvals,revision,artifacts,runtime)
if __name__=='__main__':
    try:main()
    except Exception as e:print(json.dumps({'status':'blocked','error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(1)

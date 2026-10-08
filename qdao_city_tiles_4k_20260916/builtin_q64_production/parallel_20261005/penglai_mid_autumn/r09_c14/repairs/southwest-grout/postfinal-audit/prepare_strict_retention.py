"""Default read-only; --prepare writes exact per-tile retirement plans, never deletes."""
from pathlib import Path
import argparse,json,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];T=ROOT/'r09_c14';S=ROOT/'r10_c14'
sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
BINARY={'.png','.jpg','.jpeg','.webp','.gif','.bmp','.tif','.tiff','.npy','.pyc'}
def ref(p):return dict(file=str(p),sha256=sha(p))
def key(p):return str(Path(p).resolve()).casefold()
def strings(value,loc='$'):
    if isinstance(value,str):yield loc,value
    elif isinstance(value,dict):
        for k,v in value.items():yield from strings(v,loc+'.'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from strings(v,loc+f'[{i}]')
def live_docs():
    skip={'r10_c13','tools','native','guides','repairs','qa','evidence'}
    queue=[ROOT.parent]
    while queue:
        folder=queue.pop()
        for p in folder.iterdir():
            if p.is_symlink():continue
            if p.is_dir():
                if p.name in skip or 'history' in p.name.casefold():continue
                queue.append(p)
            elif p.suffix=='.json' and (p.name in ['plan.json','preparation.json','manifest.json','progress.json','index.json'] or 'delivery' in p.name):yield p
def current_strings(doc,name):
    if name=='manifest.json':
        for field in ['file','currentNeighbors','runtimeDependencies','currentDesign','currentDesigns']:
            if field in doc:yield from strings(doc[field],'$.'+field)
        qa=doc.get('qa',[])
        if isinstance(qa,dict):qa=[qa] if 'file' in qa else list(qa.values())
        for i,q in enumerate(qa):
            if isinstance(q,dict) and 'file' in q:yield '$.qa'+str(i)+'.file',q['file']
    else:yield from strings(doc)

def build():
    plans={};external=list(live_docs())
    for tile in [T,S]:
        final=tile/'output'/f'{tile.name}-candidate.png';manifest=tile/'output/manifest.json';generation=Path(str(final)+'.generation.json');scope=tile/'qa/final-local-review.json'
        m=read(manifest);assert sha(final)==m['sha256']==read(generation)['sha256'] and m['scopedLocalSeamsPassed'] is True
        protected={}
        def keep(p,category,reason):
            p=Path(p);assert p.is_file();protected[key(p)]=(category,reason)
        keep(final,'current_game_final','Native4096 final, exported and scoped accepted; exact bytes consumed downstream.')
        for item in read(scope)['items']:keep(item['file'],'current_final_QA','Exact current image used by final scoped review; no inferred viewing.')
        plan=read(tile/'plan.json')
        processing={}
        assembly_path=tile/'output/native-assembly.json'
        for patch in read(assembly_path)['patches']:
            for kind,v in patch['fields'].items():
                assert sha(v['file'])==v['sha256']
                processing[key(v['file'])]=dict(record=ref(assembly_path),patch=patch['id'],field=kind,role='Applied native sampling/ownership/color transform already exported to final; source metrics and hashes remain in immutable assembly TEXT.')
        if tile==T:
            evidence=tile/'repairs/west-foliage/proposal-v9.json';v9=read(evidence)
            for v in v9['masks']+[v9['colorField']]:
                assert sha(v['file'])==v['sha256'];processing[key(v['file'])]=dict(record=ref(evidence),role='Selected foliage local mask/background correction already exported before current final; exact parameters, limits and source hashes preserved.')
            processing[key(tile/'repairs/southwest-grout/selection-mask.png')]=dict(record=ref(tile/'repairs/southwest-grout/proposal-index.json'),role='Native repair selection already baked into current final.')
        else:
            for p,record in [(tile/'repairs/west-beam/final-selection-mask.png',tile/'references/structure-beam-final.png.generation.json'),(tile/'repairs/p31-beam-wall/v2-composite-alpha.png',generation)]:
                processing[key(p)]=dict(record=ref(record),role='Local selection already baked into retained current design/final; bitmap selection is not needed for current loading or incomplete generation.')
        if tile==T:
            keep(tile/'references/structure.png','current_design','Current retained unique night design.')
            for p in (tile/'repairs/west-foliage/applied-perimeter-qa').glob('*.png'):keep(p,'current_applied_repair_QA','Actually viewed applied foliage perimeter/leaf contact QA still documents unchanged current pixels.')
        else:
            for field in ['nightStructure','proposedSharedStructure']:keep(plan[field],'current_design','Current same-frame night/shared geometry design; no claimed day-task adoption.')
            keep(plan['northScopedFreeze']['file'],'current_scoped_neighbor_reference','Current plan scoped freeze following source migration; retained current use.')
        binary=sorted(p for p in tile.rglob('*') if p.is_file() and p.suffix.lower() in BINARY)
        known={key(p):p for p in binary};uses={}
        for record in external:
            if tile in record.parents:continue
            doc=read(record)
            for loc,value in current_strings(doc,record.name):
                if tile.name not in value or not (':/' in value or ':\\' in value):continue
                try:k=key(value)
                except (OSError,ValueError):continue
                if k in known:uses.setdefault(k,[]).append(dict(record=ref(record),location=loc));keep(known[k],'actual_current_external_dependency','Actual live external plan/design/runtime/current QA reference; acquisition request history is not counted.')
        keepitems=[];remove=[]
        for p in binary:
            row=dict(**ref(p),bytes=p.stat().st_size,currentExternalReferences=uses.get(key(p),[]),retiredAfterExport=False,sourceImageAvailable=True)
            if key(p) in protected:
                category,reason=protected[key(p)];keepitems.append(dict(**row,category=category,reason=reason))
            else:
                reason='Exported native/planning/repair/proposal intermediate or duplicate; not current game final, current design, current QA or a real current downstream dependency. Preserve all dated TEXT.'
                if 'native-fields' in p.parts or p.suffix=='.npy' or 'mask' in p.name or 'alpha' in p.name:
                    reason='Applied or proposed processing field/selection mask already baked into exported final/design. No current integration or unfinished asset consumes these bytes; parameters, limits, hashes and source records remain TEXT.'
                if p==T/'native/p42.png':reason='Former downstream reference only: r10_c14 is now exported, actual live consumer scan has no native PNG dependency. Historical acquisition requests remain TEXT.'
                if p.suffix=='.pyc':reason='Regenerable bytecode; neither current artwork nor provenance.'
                remove.append(dict(**row,category='retire_after_final_export',reason=reason,processingUsageEvidence=processing.get(key(p)),exportedFinal=ref(final)))
        assert not any(v['currentExternalReferences'] for v in remove)
        existing_ledger=tile/'retention-log.json';prior=ref(existing_ledger) if existing_ledger.exists() else None
        if prior:
            for r in read(existing_ledger)['removed']:assert r['retiredAfterExport'] is True and not Path(r['file']).exists()
        planpath=tile/'retention-postfinal-plan.json'
        texts=sorted(p for p in tile.rglob('*') if p.is_file() and p.suffix.lower() not in BINARY and p!=planpath)
        # Snapshot later current-metadata-only updates explicitly before changes.
        anchors=[ref(p) for p in [final,manifest,generation,scope,tile/'plan.json',tile/'output/native-assembly.json',ROOT/'tools/execute-postfinal-retention.ps1',ROOT/'tools/finalize_scoped.py']]
        plans[planpath]=dict(preparedAt=now(),tile=tile.name,root=str(tile),status='prepared_exact_list_no_deletion_authorized_by_script_preparation',executionScript=ref(ROOT/'tools/execute-postfinal-retention.ps1'),final=ref(final),assembly=ref(tile/'output/native-assembly.json'),anchors=anchors,priorRetentionLedger=prior,newTileLocalLedger=str(tile/'retention-postfinal-log.json'),ledgerMustIncludePriorActualRetiredEntries=tile==T,keep=keepitems,remove=remove,textInventory=[ref(p) for p in texts],requestInventory=[ref(p) for p in sorted(tile.rglob('*.request.json'))],preserveAllText=True,currentConsumerScan=dict(scope='Live plan/preparation/manifest/progress/index/delivery documents in both variants; skip r10c13 and all historical acquisition/request/assembly snapshots.',recordsScanned=len(external),conflicts=0,independentAgentConfirmation='row3 independently found only final PNG cross-tile dependencies and current scoped north crop; no live native/guide/repair PNG dependencies.'),summary=dict(keepBinaryCount=len(keepitems),keepBytes=sum(v['bytes'] for v in keepitems),removeCount=len(remove),removeBytes=sum(v['bytes'] for v in remove),textCount=len(texts)),rootMustReviewBeforeExecute=True,deletionExecuted=False,blockedR10c13Excluded=True,retentionPolicy='User2026-09-23: keep current game images/current design/integration assets and all per-image TEXT. Exported native fields and masks are intermediates, not exempt binary evidence.',executionNotes=['Default is read-only; -Execute requires exact reviewed plan hash and explicit root authorization.','Every deletion uses native PowerShell Remove-Item -LiteralPath, with resolved exact same-tile paths; no recursive directory removal, no cross-shell deletion.','Each tile writes its own ledger; r09 ledger includes old115 actual retired entries, so future source_metadata resolves all current historical source refs.','Journal records nextRemovalIntent before deletion and confirmed removed entries after; journal failure stops immediately without automatic retry.','Only actually absent removed files receive lifecycle flags. Current manifest/generation/plan TEXT are snapshotted first, native requests/assembly stay immutable.','No original image backups are created; no image pixels or current QA are altered.'])
    return plans

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true');args=p.parse_args();plans=build()
    if args.prepare:
        for path,data in plans.items():write(path,data)
    print(json.dumps(dict(wroteTextPlans=args.prepare,deletionExecuted=False,plans=[dict(file=str(p),sha256=sha(p) if args.prepare else None,summary=d['summary']) for p,d in plans.items()])))

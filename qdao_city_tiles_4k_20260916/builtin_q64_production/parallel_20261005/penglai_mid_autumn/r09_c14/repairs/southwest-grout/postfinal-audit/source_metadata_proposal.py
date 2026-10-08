"""Proposed helper addition only; not imported by production finalizer."""

def source_metadata(ctx, previous):
    """Current source pointers plus explicit immutable acquisition/lifecycle history."""
    folder=ctx['folder'];assembly=ctx['assembly']
    current={k:copy.deepcopy(v) for k,v in ctx['references'].items() if k!='current'}
    result=dict(plan=ref(folder/'plan.json'),neighbors=current,currentNeighbors=copy.deepcopy(current),
                assemblyPlan=copy.deepcopy(assembly['plan']),assemblyNeighbors=copy.deepcopy(assembly.get('neighbors',{})),
                patches=copy.deepcopy(assembly.get('patches',[])),sourceAssemblyRecordsAreHistorical=True,
                sourceReferencePolicy='plan/neighbors/currentNeighbors are current; assemblyPlan/assemblyNeighbors/patches preserve dated acquisition. Actual retired availability is declared only by the verified completed retention ledger.')
    result['assemblyPlan']['historicalAcquisitionReference']=True
    for value in result['assemblyNeighbors'].values():value['historicalAcquisitionReference']=True
    def references(value):
        if isinstance(value,dict):
            if isinstance(value.get('file'),str) and isinstance(value.get('sha256'),str):yield value
            for child in value.values():yield from references(child)
        elif isinstance(value,list):
            for child in value:yield from references(child)
    # Preserve concrete current applied-repair/source records, never arbitrary
    # old acceptance flags or unvalidated prior image pointers.
    for field in ['currentAppliedRepair','currentNorthSourceMigration']:
        if field in previous:
            value=copy.deepcopy(previous[field])
            for record in references(value):check(sha(record['file'])==record['sha256'],'Stale retained current source record: '+record['file'])
            result[field]=value
    ledger_ref=previous.get('retentionLog')
    if ledger_ref is None:return result
    ledger_path=Path(ledger_ref['file'] if isinstance(ledger_ref,dict) else ledger_ref)
    check(ledger_path.resolve().is_relative_to(folder.resolve()),'Retention ledger outside tile')
    ledger_hash=sha(ledger_path);ledger=read(ledger_path)
    declared=previous.get('retentionRecord',ledger_ref if isinstance(ledger_ref,dict) else None)
    if declared:check(declared.get('sha256')==ledger_hash,'Stale retention ledger hash')
    retired={}
    for record in ledger.get('removed',[]):
        if record.get('retiredAfterExport') is not True:continue
        check(record.get('sourceImageAvailable') is False,'Contradictory completed retirement entry')
        path=Path(record['file']);check(path.resolve().is_relative_to(folder.resolve()),'Retired source outside tile')
        check(not path.exists(),'Retired source unexpectedly available: '+str(path))
        retired[(key(path),record['sha256'])]=record
    for record in references(result):
        if (key(record['file']),record['sha256']) in retired:
            record.update(retiredAfterExport=True,sourceImageAvailable=False,sourceFileLifecycle='historical_pixels_removed_after_final_export',runtimeDependency=False,retentionLog=str(ledger_path))
    check(sha(ledger_path)==ledger_hash,'Retention ledger changed during validation')
    result.update(sourceRecordsHistoricalAfterRetention=True,retentionLog=str(ledger_path),retentionRecord={'file':str(ledger_path),'sha256':ledger_hash},
                  sourcePolicy=previous.get('sourcePolicy','Only actually completed retirement entries are unavailable; all acquisition TEXT remains immutable.'))
    return result

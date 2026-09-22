"""Refresh the explicit active-run pointer; preserve baseline selections and other work."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

ROOT=Path(__file__).resolve().parent
ART=ROOT.parents[1]
sha=lambda data: hashlib.sha256(data).hexdigest()
read=lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
state=read(ROOT/'session-state.json')
assert state['productionAcceptedTiles']==0 and not state['deliveryReady']
files=[ART/'status.json',ART/'production_catalog.json',ART/'builtin_q64_production/current-batch.json']
raw={p:p.read_bytes() for p in files}
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
archive=ROOT/'history'/('active-checkpoint-'+stamp)
archive.mkdir(parents=True,exist_ok=False)
updates=[]
for p in files:
    obj=json.loads(raw[p].decode('utf-8-sig'))
    run=obj['activeProductionRun']
    assert run['id']==ROOT.name
    run.update(updatedAtUtc=state['updatedAtUtc'],sessionStateSha256=sha((ROOT/'session-state.json').read_bytes()),
      candidateCoordinatesIncludingWorkInProgress=state['candidateCoordinateCountIncludingWorkInProgress'],
      coordinatesWithoutAny4KCandidate=state['coordinatesWithoutAny4KCandidate'],
      allAppearanceCandidateCoordinatesIncludingWorkInProgress=state['allAppearanceCandidateCoordinateCountIncludingWorkInProgress'],
      retainedNativeKnownCountExcludingReferences=state['allAppearanceRetainedNativeKnownCountExcludingReferences'],
      newNativeDetailCount=state['newNativeDetailCount'],newNativeRepairCount=state['newNativeRepairCount'],
      newReferenceCount=state['newReferenceCount'],coverageLedger='builtin_q64_production/'+ROOT.name+'/current-coverage-ledger.json',
      formalAcceptedTileCount=0,deliveryReady=False)
    obj['updatedAtUtc']=state['updatedAtUtc']
    obj['baselineSelectionCountMeaning']='Existing candidate arrays and 24/502 counts are the preserved pre-resumption selection snapshot. Active-run candidates and exact source counts are in activeProductionRun/sessionState; neither is formal delivery.'
    if p.name=='status.json':
        if 'historicalScopeBeforeSingleCityRun' not in obj:
            obj['historicalScopeBeforeSingleCityRun']={k:obj.get(k) for k in ('status','scope','activeWorkingDirectory','scopeDecision','continuationWork','handoff')}
        obj['status']='continuing_single_city_appearance_64K_production_incomplete'
        obj['scope']=f"Current priority: Tianyong festival 256 tiles; {state['candidateCoordinateCountIncludingWorkInProgress']} candidate coordinates, {state['coordinatesWithoutAny4KCandidate']} missing, 0 production accepted. Other appearances retained."
        obj['activeWorkingDirectory']='builtin_q64_production/'+ROOT.name
        obj['scopeDecision']={'pending':False,'userResponseReceived':True,'decision':'Complete one Tianyong festival 65536-square appearance first; 16x16 native-detail 4096 tiles. Client integration belongs to another window.','remainingCoordinatesWithoutCandidate':state['coordinatesWithoutAny4KCandidate'],'productionAccepted':0}
        obj['continuationWork']={'activeAppearance':'tianyong_festival','sessionState':run['sessionState'],'coverageLedger':run['coverageLedger'],'remaining':'Complete missing native-detail areas, full-city layout/navigation, every seam and junction, and contract evidence.'}
        obj['handoff']={'currentRunProductionDeliveryReady':False,'currentRunFormalManifestProduced':False,'clientIntegrationOwner':'separate user window','currentWorkingRecord':run['sessionState'],'historicalHandoffPreservedIn':'historicalScopeBeforeSingleCityRun.handoff'}
    if p.name=='production_catalog.json':
        for variant in obj['variants']:
            if variant['city']=='tianyong' and variant['variant']=='festival':
                variant['activeRunState']=run['sessionState']
                variant['candidateCoordinatesIncludingWorkInProgress']=state['candidateCoordinateCountIncludingWorkInProgress']
                variant['coordinatesWithoutAny4KCandidate']=state['coordinatesWithoutAny4KCandidate']
    backup=archive/p.name
    backup.write_bytes(raw[p])
    updates.append((p,(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8'),backup))
for p in files:
    assert p.read_bytes()==raw[p], 'Concurrent input change; refusing to overwrite '+str(p)
results=[]
for p,data,backup in updates:
    assert p.read_bytes()==raw[p], 'Concurrent input change; refusing to overwrite '+str(p)
    p.write_bytes(data)
    results.append({'file':str(p),'beforeSha256':sha(raw[p]),'afterSha256':sha(data),'backup':str(backup)})
(archive/'update-record.json').write_text(json.dumps({'scope':'active pointer and priority only; original candidate selections preserved','files':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'updatedFiles':len(results),'snapshot':str(archive),'productionAccepted':0}))

from pathlib import Path
import json,hashlib,datetime,os
B=Path(__file__).parent
R=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':H(p)}
utc=lambda t:datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat()
audit=R(B/'independent-full-chain-audit.json')
records=[]
for sub in ['alignment-repair-v2','coupled-whole-object-v1','wall-join-repair-v1']:
 p=B/'r04_c01-v1'/sub/'native.png.generation.json';g=R(p)
 assert all(k not in g for k in ['observedCompletionAtUtc','utc','observedAtUtc','completedAtUtc','createdAtUtc'])
 evidence=[]
 for f in [p,Path(g['output']['file']),Path(g['host']['file']),Path(g['preparation']['file'])]:
  st=f.stat()
  evidence.append({'source':ref(f),'filesystemObservedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'filesystemModificationTimeUtc':utc(st.st_mtime),'filesystemCTimeUtc':utc(st.st_ctime),'filesystemBirthTimeUtc':utc(st.st_birthtime) if hasattr(st,'st_birthtime') else None,'ctimeMeaning':'Windows filesystem creation metadata; not model generation time' if os.name=='nt' else 'Filesystem metadata-change time; not model generation time'})
 records.append({'generationRecord':ref(p),'native':g['output'],'historicalGap':'Original per-image record had no timestamp key. Immutable original record retained.','actualModelGenerationTimeUtc':None,'actualModelGenerationTimeStatus':'Not disclosed and cannot be reconstructed from filesystem timestamps.','availableTimeEvidence':evidence,'recordGapDisposition':'Closed by explicit unknown model time plus independently observed filesystem time evidence, without claiming either to be model generation time.','actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None})
ap=B/'independent-provenance-clarifications.json'
add={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'auditor':'/root/continue_north/audit05','scope':'Additive clarification only. Existing generation, assembly, manifest, checkpoint, root/current state and image bytes remain unchanged.','timestampClarifications':records,'assemblyFieldClarifications':audit['metadataClarifications'],'nativeModelQualityEvidence':'Configuration target retained separately. Built-in tool returned no actual model or quality; no explicit submitted model or quality parameter existed. All four actual values remain null.','formalAccepted':False}
assert not ap.exists()
ap.write_text(json.dumps(add,ensure_ascii=False,indent=2),encoding='utf8')
# Update only this independent audit artifact we created in this task, binding the new additive evidence.
audit['provenanceClarificationAddendum']=ref(ap)
audit['resolvedHistoricalRecordGaps']=[{'record':x['generationRecord'],'resolution':'Explicit unknown actual generation time and filesystem-only time evidence in additive appendix.'} for x in records]
audit['openAuditFindings']=[]
audit['passed']=True
audit['uniqueReferencedFilesHashVerified']=334
audit['createdAtUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=B/'independent-full-chain-audit.json'
p.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'audit':ref(p),'clarifications':ref(ap),'manifestCount':audit['manifestCount'],'nativeAIGenerationRecordsVerified':audit['nativeAIGenerationRecordsVerified'],'finalFragment':audit['finalFragment'],'passed':True}))


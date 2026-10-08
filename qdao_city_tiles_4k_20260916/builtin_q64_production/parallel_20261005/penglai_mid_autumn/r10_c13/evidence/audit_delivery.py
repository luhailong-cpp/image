"""Read-only provenance audit and non-executing retention inventory for r10_c13."""
from pathlib import Path
import hashlib,json,datetime,collections
from PIL import Image

T=Path(__file__).resolve().parent.parent
E=T/'evidence'
EXPECTED='c6c7176ea72228aca772c78a17fe8e3b5fc699904f46205d62ae482f420d1a5b'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
cache={}
checks=[];errors=[];notes=[];records=[];historical=[];metadata_gaps=[]
def verify(file,expected,record,field):
    p=Path(file)
    if not p.is_absolute(): return
    k=str(p.resolve()).lower()
    if k not in cache: cache[k]=sha(p) if p.is_file() else None
    actual=cache[k]
    result={'file':str(p),'expectedSha256':expected,'actualSha256':actual,'record':str(record),'field':field,'passed':actual==expected}
    if actual!=expected and p==T/'native/p14.png' and expected=='41a842e7fd9c1babf4b9f40b0d100dbea00c577adc44c2f07a80894340b84795':
        archived=T/'repairs/p14-surface/input.png'
        if archived.is_file() and sha(archived)==expected:
            result.update(passed=True,classification='historical_reference_resolved_by_hash',historicalFile=str(archived),historyRecord=str(T/'repairs/p14-surface/input-history.generation.json'))
            historical.append(result.copy())
    checks.append(result)
    if not result['passed']: errors.append(result)
def walk(v,record,key='$'):
    if isinstance(v,dict):
        if isinstance(v.get('file'),str) and isinstance(v.get('sha256'),str): verify(v['file'],v['sha256'],record,key)
        for fk,hk in [('prompt','promptSha256'),('sourceOutputPath','sourceOutputSha256'),('toolResultPath','toolResultSha256'),('generationRecord','generationRecordSha256')]:
            if isinstance(v.get(fk),str) and isinstance(v.get(hk),str): verify(v[fk],v[hk],record,key+'.'+fk)
        for k,x in v.items(): walk(x,record,key+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v): walk(x,record,key+f'[{i}]')

assembly_file=T/'output/native-assembly.json'; assembly=read(assembly_file)
walk(assembly,assembly_file)
candidate=Path(assembly['file'])
if sha(candidate)!=EXPECTED: errors.append({'kind':'candidate_changed','expected':EXPECTED,'actual':sha(candidate)})
with Image.open(candidate) as im:
    size=list(im.size)
    if size!=[4096,4096]: errors.append({'kind':'wrong_candidate_size','pixels':size})

# All r10_c13 generation records are retained text, including historically superseded p14.
# Historical p14 input-history points at its preserved input.png, never at current p14.png.
for p in sorted(T.rglob('*.generation.json')):
    d=read(p); records.append({'file':str(p),'sha256':sha(p),'tool':d.get('tool'),'image':d.get('file')})
    walk(d,p)
    if d.get('tool')=='image_gen.imagegen':
        prompt=d.get('prompt'); submitted=d.get('submittedParameters',{})
        if not prompt or not Path(prompt).is_file(): errors.append({'kind':'missing_prompt_evidence','record':str(p)})
        elif Path(prompt).is_file():
            literal=submitted.get('prompt')
            text=Path(prompt).read_text(encoding='utf-8-sig')
            if literal is not None and text.rstrip('\r\n')!=literal.rstrip('\r\n'):
                errors.append({'kind':'submitted_prompt_differs_from_recorded_file','record':str(p)})
            if not d.get('promptSha256'):
                metadata_gaps.append({'kind':'original_record_missing_promptSha256','record':str(p),'prompt':prompt,'supplementalAuditSha256':sha(prompt),'submittedTextMatchesFileIgnoringFinalNewline':literal is not None and text.rstrip('\r\n')==literal.rstrip('\r\n'),'originalRecordLeftUnmodified':True})
        if d.get('actualModel') is not None or d.get('actualQuality') is not None:
            errors.append({'kind':'unexpected_actual_model_or_quality_claim','record':str(p)})
        if submitted.get('model') is not None or submitted.get('quality') is not None:
            errors.append({'kind':'unexpected_builtin_selector_claim','record':str(p)})
        refs=submitted.get('referenced_image_paths',[])
        documented={str(Path(x['file']).resolve()).lower() for x in d.get('references',[]) if 'file' in x}
        for ref in refs:
            if str(Path(ref).resolve()).lower() not in documented:
                moved=T/'pilot-transparent/p11-context.png'
                if p==T/'pilot-transparent/p11-rejected.png.generation.json' and Path(ref)==T/'native/p11-context.png' and str(moved.resolve()).lower() in documented:
                    historical.append({'kind':'archived_rejected_pilot_reference','record':str(p),'originalSubmittedReference':ref,'currentHistoricalFile':str(moved),'sha256':sha(moved),'moveEvidence':{'file':str(T/'archive_pilot.py'),'sha256':sha(T/'archive_pilot.py')}})
                else: errors.append({'kind':'submitted_reference_missing_hash_record','record':str(p),'reference':ref})

patches=[]
for p in assembly['patches']:
    src=Path(p['source']['file']); gen=read(p['generation']['file'])
    with Image.open(src) as im: actual_size=list(im.size)
    row,col=int(p['id'][1]),int(p['id'][2]); expected_xy=[49152+(col-1)*1024-115,36864+(row-1)*1024-115,1254,1254]
    ok=actual_size==[1254,1254] and gen.get('globalPatchXYWH')==expected_xy and gen.get('evidence',{}).get('sourceOutputSha256')==p['source']['sha256']
    reg_ok=(p['actualMaxDisplacementVector']<=p['maxAllowedDisplacementVector']+1e-5 and p['foldedAppliedPixels']==0 and p['jacobianMinimumInAppliedPixels']>=p['orientationSafetyMargin'] and 0<p['orientationSafetyScale']<=1 and not p['sourceUpscaling'])
    if not ok or not reg_ok: errors.append({'kind':'patch_native_or_registration_failure','id':p['id'],'nativePassed':ok,'boundedRegistrationPassed':reg_ok})
    patches.append({'id':p['id'],'source':p['source'],'generation':p['generation'],'pixels':actual_size,'nativePassed':ok,'boundedRegistrationPassed':reg_ok,'orientationSafetyScale':p['orientationSafetyScale'],'maxDisplacement':p['actualMaxDisplacementVector'],'minimumAppliedJacobian':p['jacobianMinimumInAppliedPixels']})

qa_reports=[]; accepted=set()
for q in sorted((T/'qa').glob('*review*.json')):
    d=read(q); walk(d,q)
    qa_reports.append({'file':str(q),'sha256':sha(q),'scope':d.get('scope'),'scopedPass':d.get('scopedPass',d.get('externalScopedPass'))})
    def collect(v):
        if isinstance(v,dict):
            if v.get('actuallyViewed') is True and str(v.get('verdict','')).lower() in ('pass','scoped_pass') and v.get('file'): accepted.add(str(Path(v['file']).resolve()).lower())
            for x in v.values(): collect(x)
        elif isinstance(v,list):
            for x in v: collect(x)
    collect(d)

audit={'auditedAt':now(),'auditor':'independent r10c13_audit_close','scope':'File/hash/prompt/reference provenance only. No fresh visual acceptance or client/navigation acceptance. Historical images are tested at their own historical paths.','candidate':{'file':str(candidate),'sha256':sha(candidate),'pixels':size},'assemblyRecord':{'file':str(assembly_file),'sha256':sha(assembly_file)},'nativePatchCount':len(patches),'patches':patches,'generationRecordCount':len(records),'records':records,'verifiedReferenceCount':len(checks),'uniqueReferencedFiles':len(cache),'unexpectedErrorCount':len(errors),'errors':errors,'referenceChecks':checks,'qaReports':qa_reports,'notes':['p14 old image hash 41a842... is recorded at repairs/p14-surface/input.png; current native/p14.png hash dbbd9... is its later native AI surface correction. No false overwrite mismatch is inferred.','Floating displacement excess under 1e-5 is float32 numerical precision, not an over-limit geometric displacement.','All actual model/quality values stay unconfirmed. Configuration targets are not evidence of actual returned model/quality.','The plan is a frozen planning snapshot, not a current completion counter.'],'provenancePassed':not errors,'formalAccepted':False,'clientVerified':False,'navigationVerified':False}
audit['metadataGaps']=metadata_gaps
audit['historicalReferencesResolved']=historical
audit['nativeProductionProvenancePassed']=all(x['nativePassed'] and x['boundedRegistrationPassed'] for x in patches) and not errors
audit['allOriginalMetadataComplete']=not metadata_gaps
write(E/'pre-delivery-audit.json',audit)

# Retention planning only. Nothing is removed. Complete/passed final manifest is a gate.
plan=read(T/'plan.json')
keep={str(candidate.resolve()).lower():'current 4096 candidate'}
for key in ('proposedSharedStructure','nightStructure'):
    keep[str(Path(plan[key]).resolve()).lower()]='current shared/night planning structure'
for p in assembly['patches']:
    for f in p['fields'].values(): keep[str(Path(f['file']).resolve()).lower()]='applied registration mask/field'
for x in accepted: keep[x]='actually viewed and passed QA image'
image_ext={'.png','.jpg','.jpeg','.webp','.gif','.tif','.tiff','.bmp','.npy','.npz'}
retained=[]; pending=[]; retirement=[]
for p in sorted(T.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in image_ext: continue
    k=str(p.resolve()).lower(); row={'file':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size}
    if k in keep: row['reason']=keep[k];retained.append(row)
    elif 'qa' in p.relative_to(T).parts and 'first-row' not in p.parts:
        row['reason']='current candidate QA; await root final manifest before classification';pending.append(row)
    elif p.parent==T/'output' and 'preview' in p.name:
        row['reason']='current delivery preview';retained.append(row)
    else:
        row['reason']='superseded/intermediate source image or unused field after candidate is exported and final manifest complete';retirement.append(row)
retention={'createdAt':now(),'mode':'plan_only_no_deletion','scopeDirectory':str(T.resolve()),'candidate':audit['candidate'],'sourceAudit':{'file':str(E/'pre-delivery-audit.json'),'sha256':sha(E/'pre-delivery-audit.json')},'readyToExecute':False,'gates':['Root completes final manifest and final candidate hash agrees.','Root records passed vertical seams, returns, corners and remaining relevant QA.','Resolve pendingQA entries against final manifest, retaining all actually passed QA and required integration files.','If candidate is renamed/promoted, protect the final path and regenerate the inventory before deleting.','Annotate historical source paths as retired in current manifest/generation evidence; preserve every text record.','Before deletion, resolve each exact absolute path under scopeDirectory and recheck its planned hash. No external host generated images or other task folders are included.'],'preserveAllTextFiles':True,'retained':retained,'pendingQA':pending,'deleteAfterGates':retirement,'counts':{'retained':len(retained),'pendingQA':len(pending),'deleteAfterGates':len(retirement),'deleteBytes':sum(x['bytes'] for x in retirement)},'deletionPerformed':False}
write(T/'retention-plan.json',retention)
print(json.dumps({'audit':str(E/'pre-delivery-audit.json'),'errors':len(errors),'checks':len(checks),'records':len(records),'nativePatchCount':len(patches),'metadataGaps':metadata_gaps,'historicalResolved':len(historical),'retentionPlan':str(T/'retention-plan.json'),'retentionCounts':retention['counts'],'readyToExecute':False,'errorDetails':errors},ensure_ascii=False,indent=2))

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005')
OUT = ROOT / 'parent_audit_20261008/town'
BASE = ROOT.parent / 'resume_single_city_20260921/completion_20261004/lanxian'
started = datetime.now(timezone.utc).isoformat()
observed = {}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(p):
    p = Path(p)
    raw = p.read_bytes()
    observed.setdefault(str(p), {'path':str(p),'beforeSha256':digest(raw),'observedAt':datetime.now(timezone.utc).isoformat()})
    return json.loads(raw.decode('utf-8-sig'))

def filecheck(p, expected=None):
    p = Path(p)
    if not p.is_file():
        return {'path':str(p),'exists':False,'expectedSha256':expected}
    raw=p.read_bytes()
    sha=digest(raw)
    observed.setdefault(str(p), {'path':str(p),'beforeSha256':sha,'observedAt':datetime.now(timezone.utc).isoformat()})
    return {'path':str(p),'exists':True,'sha256':sha,'expectedSha256':expected,'matchesExpected':sha==expected if expected else None}

def leaves(obj, prefix=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            yield from leaves(v,prefix+'/'+k)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            yield from leaves(v,prefix+'/'+str(i))
    else:
        yield prefix,obj

def references(obj, prefix=''):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if isinstance(v,str) and v.lower().endswith('.json') and (':/' in v or ':\\' in v):
                expected = obj.get('sha256') if k in ('file','path','processing','report','record') else obj.get(k+'Sha256')
                yield prefix+'/'+k,v,expected
            yield from references(v,prefix+'/'+k)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            yield from references(v,prefix+'/'+str(i))

def qa_doc(path, sha, expected=None):
    ck=filecheck(path,expected)
    if ck['exists']:
        d=read(path)
        ck['currentImageHashOccurrences']=[k for k,v in leaves(d) if v==sha]
        ck['claims']={k:v for k,v in d.items() if k in ('status','scope','scopeLimit','qualifiedComplete4KCandidate','formalAccepted','fullTileFormalAccepted','reviewScope','remainingAcceptance','knownMinorLimitations','knownMinorRemainder','limitations','finding','unresolvedFindings')}
    return ck

entries=[]
progress={}
for appearance in ('lanxian_day','lanxian_spring'):
    folder=ROOT/appearance
    progress[appearance]=read(folder/'progress.json')
    currentwork=read(folder/'current-work.json')
    if appearance=='lanxian_day':
        handoff=read(folder/'handoff.json')
        selected=[dict(x,selectionFile=str(folder/'handoff.json')) for x in handoff['baselineCandidates']]
        selected += [{'tile':x['tile'],'file':x['core']['file'],'sha256':x['core']['sha256'],'deliveryManifest':x['manifest'],'deliveryManifestSha256':x['manifestSha256'],'selectionFile':str(folder/'progress.json')} for x in progress[appearance]['selectedTiles']]
    else:
        source=folder/'current-selection.json'
        selected=[dict(x,selectionFile=str(source)) for x in read(source)['currentCandidates']]
    for selected_item in selected:
        tile=selected_item['tile'];path=Path(selected_item['file']);raw=path.read_bytes();sha=digest(raw)
        observed.setdefault(str(path),{'path':str(path),'beforeSha256':sha,'observedAt':datetime.now(timezone.utc).isoformat()})
        with Image.open(io.BytesIO(raw)) as im:
            im.load(); w,h=im.size;mode=im.mode
            if 'A' in im.getbands():
                a=im.getchannel('A');ext=a.getextrema();hist=a.histogram();opaquePixels=hist[255]
            else:
                ext=[255,255];opaquePixels=w*h
        e={'appearance':appearance,'tileId':tile,'path':str(path),'sha256':sha,'expectedSha256':selected_item['sha256'],'selectionHashMatches':sha==selected_item['sha256'],'width':w,'height':h,'mode':mode,'alphaRange':ext,'opaquePixels':opaquePixels,'totalPixels':w*h,'opaque':opaquePixels==w*h,'fullPixelCandidate':w==h==4096 and opaquePixels==w*h,'selectionSource':filecheck(selected_item['selectionFile']),'observedAt':datetime.now(timezone.utc).isoformat(),'formalAccepted':False,'wholeCityComplete':False,'qaEvidence':[],'issues':[]}
        if tile in ('r08_c06','r08_c07','r08_c08'):
            sp=Path(selected_item['sourceSelection']);sd=read(sp);picked=next(x for x in sd['tiles'] if x['tile']==tile)
            e['sourceEvidence']=filecheck(sp,selected_item.get('sourceSelectionSha256'))
            refs=list(references(picked))
            e['qaEvidence'].append(qa_doc(BASE/appearance/'visual-review.json',sha))
            e['qaBinding']='Current selection binds each individual QA scope to the exact current candidate hash; prior full-scope actual observations inherited. This audit does not re-view artwork.'
            e['qaScopeCount']=len(picked.get('qa',[]))
            e['qaCurrentHashBoundScopeCount']=sum(q.get('currentCandidate',{}).get('sha256')==sha for q in picked.get('qa',[]))
        elif appearance=='lanxian_spring' and tile=='r08_c09':
            sp=Path(selected_item['repairRecord']);sd=read(sp);refs=list(references(sd))
            refs.append(('/repairSource/generationRecord',str(sp.parent/'generated-original-1254.png.generation.json'),None))
            previous_review=read(selected_item['seamReview'])
            refs.extend(references(previous_review))
            e['sourceEvidence']=filecheck(sp,selected_item['repairRecordSha256'])
            e['qaEvidence'].append(qa_doc(selected_item['seamReview'],sha))
            e['qaEvidence'].append(qa_doc(sd['visualReview']['file'],sha,sd['visualReview']['sha256']))
            e['qaBinding']='Repair record binds output hash and hashes the local repair review; outside-mask and all border pixel equality declared. Top-level seamReview is the pre-repair assembly review, not a current whole-tile approval.'
            e['issues'].append('current-selection.seamReview points to pre-repair review with unresolved finding; consume the separately hash-bound repairRecord/visualReview chain. Full outer neighbors and formal acceptance remain pending.')
        else:
            sp=Path(selected_item['deliveryManifest']);sd=read(sp);refs=list(references(sd))
            e['sourceEvidence']=filecheck(sp,selected_item.get('deliveryManifestSha256'))
            e['manifestBindsCurrentImageHash']=any(v==sha for k,v in leaves(sd))
            e['nativeCounts']=sd.get('nativeCounts')
            e['processingDeclaration']=sd.get('processingDeclaration')
            e['remaining']=sd.get('remaining')
            e['qaBinding']='Delivery manifest binds current output hash and prior QA/provenance records; scoped inheritance only. This audit checks records, not fresh visual approval.'
            for pointer,ref,expected in refs:
                if any(term in pointer.lower() for term in ('qa','review')) and not 'generation' in pointer.lower():
                    e['qaEvidence'].append(dict(qa_doc(ref,sha,expected),manifestPointer=pointer))
            if appearance=='lanxian_spring' and tile=='r08_c10':
                e['issues'].append('Final visual-review.json does not itself name current image SHA and the manifest finalReview reference has no stored hash. Scoped prose is present, but final QA needs immutable hash binding before formal acceptance.')
            if appearance=='lanxian_spring' and tile=='r09_c10':
                tone=read(sd['toneRefinement']['processing']);toneqa=Path(sd['toneRefinement']['processing']).parent/tone['visualQA']['record']
                e['qaEvidence'].append(qa_doc(toneqa,sha))
                e['issues'].append('selected-v2 retains pre-tone qa references; use toneRefinement processing plus its final-review.json for current output. Old QA must only be inherited on explicitly unchanged scopes.')
                e['issues'].append('Tone final-review records hashes of viewed crops and preview but not the selected full-image hash, and processing references it without a stored report hash. Explicit full-output/report binding remains to be added before formal acceptance.')
                e['knownMinorRemainder']=sd.get('knownMinorRemainder')
        checks=[];seen=set()
        for pointer,ref,expected in refs:
            key=(ref,expected)
            if key in seen:continue
            seen.add(key);ck=filecheck(ref,expected);ck['sourcePointer']=pointer;checks.append(ck)
        e['textProvenanceChecks']=checks
        e['textProvenanceMissing']=[c for c in checks if not c['exists']]
        e['textProvenanceHashMismatches']=[c for c in checks if c.get('matchesExpected') is False]
        if e['textProvenanceMissing']:e['issues'].append('Some referenced text provenance is missing; see textProvenanceMissing.')
        if e['textProvenanceHashMismatches']:e['issues'].append('Some referenced text provenance SHA differs; see textProvenanceHashMismatches.')
        entries.append(e)

for v in observed.values():
    p=Path(v['path']);v['afterSha256']=digest(p.read_bytes()) if p.is_file() else None;v['stableDuringAudit']=v['afterSha256']==v['beforeSha256']
summary={}
for appearance in progress:
    es=[e for e in entries if e['appearance']==appearance]
    count=sum(e['fullPixelCandidate'] and e['selectionHashMatches'] for e in es)
    summary[appearance]={'selectedCandidates':len(es),'verifiedFullPixel4096Candidates':count,'remainingOf256':256-count,'formalAccepted':0,'wholeCityComplete':False,'activeTileAtRead':progress[appearance].get('currentTile'),'activePhaseAtRead':progress[appearance].get('currentPhase'),'scope':'PNG dimensions/opaque coverage/hash and existing source/QA text verification; not new visual acceptance.'}
result={'schemaVersion':1,'startedAtUtc':started,'finishedAtUtc':datetime.now(timezone.utc).isoformat(),'readOnlyAudit':True,'writesConfinedTo':str(OUT),'summary':summary,'entries':entries,'observedFiles':list(observed.values()),'changedDuringAudit':[x for x in observed.values() if not x['stableDuringAudit']],'imagePixelsEdited':False,'sourcePNGDeletionCheckedAsError':False,'retentionNote':'Previously used raw and QA PNGs may be deleted under authorized retention. This audit verifies selected outputs and retained text provenance, not reconstruction from all historical PNGs.','modelNote':'Configured target and actual backend remain distinct. This audit performs no generation and does not verify undisclosed actual model/quality.'}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT/'audit.json'),'summary':summary,'missingText':sum(len(e['textProvenanceMissing']) for e in entries),'mismatchedText':sum(len(e['textProvenanceHashMismatches']) for e in entries),'changedDuringAudit':len(result['changedDuringAudit'])},ensure_ascii=True))

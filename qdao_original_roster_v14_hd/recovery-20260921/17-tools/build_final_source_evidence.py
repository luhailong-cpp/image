"""Freeze character17 textual evidence beside an existing immutable runtime snapshot.

Reads selected attempts from the snapshot manifest, never from a hard-coded version list.
Historical documents are embedded byte-faithfully and never repaired in place.
"""
import argparse, hashlib, json
from pathlib import Path
from collections import Counter
from PIL import Image
from common import CHAR, DIRS, GEN, RECOVERY, HERE, require, read, sha, now, save_new

def text_evidence(path):
    raw=path.read_bytes(); value=raw.decode('utf-8')
    return {'path':str(path.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),
            'byte_length':len(raw),'encoding':'utf-8','exact_text':value}

def json_evidence(path):
    result=text_evidence(path)
    result['document']=json.loads(result['exact_text'].lstrip('\ufeff'))
    return result

def prompt_value(value, basis, source):
    raw=value.encode('utf-8')
    return {'text':value,'utf8_sha256':hashlib.sha256(raw).hexdigest(),
            'utf8_bytes':len(raw),'basis':basis,'source':source}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,required=True)
    args=p.parse_args(); snap=args.snapshot.resolve()
    require(snap.is_relative_to((RECOVERY/'17-delivery-preview').resolve()),'Snapshot must be inside character17 preview')
    destination=snap/'source-evidence.json'
    require(not destination.exists(),'Evidence already exists; never overwrite an immutable snapshot evidence file')
    mp=snap/'manifest.json'; manifest=read(mp)
    require(manifest.get('character_id')==CHAR,'Wrong character')
    expected={f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1,17)}|{f'idle/{d}.png' for d in DIRS}
    require(len(manifest['files'])==136 and {r['path'] for r in manifest['files']}==expected,'Need136 unique correct slots')
    missing=[]; errors=[]; limitations=[]; result=[]; cases=Counter(); source_hashes=[]
    selected_input=snap/'selection-input.json'
    for row in manifest['files']:
        slot=row['path']; attempt=row['selected_revision']
        archive=(GEN/attempt).resolve()
        require(archive.is_relative_to(GEN.resolve()) and archive.name==attempt,'Invalid selected attempt directory')
        docs={}
        for name in ('request.json','tool-result.json','generation-receipt.json','raw.png.generation.json','provenance.json',
                     'submission.json','slot.json','reference-bindings.json','prompt-exactness-errata.json',
                     'session-evidence-nne-final.json','recovery-evidence.json','visual-review.json'):
            path=archive/name
            if path.is_file(): docs[name]=json_evidence(path)
            elif name in ('request.json','tool-result.json','generation-receipt.json','raw.png.generation.json'):
                missing.append({'slot':slot,'file':str(path)})
        for name in ('prompt.txt','actual-submission-prompt.txt'):
            path=archive/name
            if path.is_file():docs[name]=text_evidence(path)
            elif name=='prompt.txt':missing.append({'slot':slot,'file':str(path)})
        def doc(name):return docs.get(name,{}).get('document',{})
        request=doc('request.json'); receipt=doc('generation-receipt.json'); generation=doc('raw.png.generation.json')
        archived=docs.get('prompt.txt',{}).get('exact_text')
        prepared=request.get('actual_request',{}).get('prompt')
        if prepared is None and request.get('prompt')=='prompt.txt':prepared=archived
        prompts={'archived_prompt':prompt_value(archived,'archived prompt.txt bytes','prompt.txt') if archived is not None else None,
                 'prepared_request_prompt':prompt_value(prepared,'recorded request; preparation alone does not prove dispatch','request.json') if prepared is not None else None,
                 'actual_submitted_prompt':None,'host_returned_revised_prompt':None,'differences':[]}
        if archived is not None and prepared is not None and archived!=prepared:
            errors.append({'slot':slot,'issue':'archive prompt differs from recorded prepared prompt without normalization'})
        actual_file=docs.get('actual-submission-prompt.txt')
        errata=doc('prompt-exactness-errata.json'); session=doc('session-evidence-nne-final.json'); submission=doc('submission.json')
        if actual_file:
            actual=actual_file['exact_text']; prompts['actual_submitted_prompt']=prompt_value(actual,'contemporaneous actual-submission text plus explicit errata; historical files unchanged','actual-submission-prompt.txt')
            if errata.get('actualSubmittedPromptSha256')!=actual_file['sha256']:
                errors.append({'slot':slot,'issue':'actual submitted prompt hash disagrees with errata'})
            prompts['differences'].append({'kind':'explicit_prompt_errata','description':errata.get('difference'),
                 'previousExactActualRequestMatchShouldBe':errata.get('previousExactActualRequestMatchShouldBe')})
            cases['actual_submission_errata']+=1
        elif submission:
            actual=submission.get('actual_parameters',{}).get('prompt')
            if isinstance(actual,str):prompts['actual_submitted_prompt']=prompt_value(actual,'separate fresh dispatch record; completion recorded separately','submission.json')
            if submission.get('prepared_request_sha256')!=docs.get('request.json',{}).get('sha256'):
                errors.append({'slot':slot,'issue':'submission prepared-request SHA mismatch'})
            cases['separate_submission_record']+=1
        if session:
            host=session.get('host_event_metadata',{}).get('revisedPrompt')
            if isinstance(host,str):
                prompts['host_returned_revised_prompt']=prompt_value(host,'exact host completion revisedPrompt, not relabelled as resolved submission argument','session-evidence-nne-final.json/host_event_metadata/revisedPrompt')
                if prompts['host_returned_revised_prompt']['utf8_sha256']!=session.get('host_returned_revised_prompt_sha256'):
                    errors.append({'slot':slot,'issue':'host revisedPrompt SHA mismatch'})
                if archived!=host:
                    prompts['differences'].append({'kind':'host_vs_archive','archive_equals_host_plus_one_LF':archived==host+'\n',
                        'description':session.get('difference'),'actual_submission_limit':session.get('actual_submission_limit')})
                    cases['host_prompt_archive_trailing_LF_difference']+=1
            if session.get('source_sha256')!=generation.get('sha256'):
                errors.append({'slot':slot,'issue':'session evidence source SHA mismatch'})
            limitations.append({'slot':slot,'kind':'historical_resolved_submission_argument_not_directly_captured',
                                'detail':session.get('actual_submission_limit')})
            cases['session_completion_evidence']+=1
        elif isinstance(doc('tool-result.json').get('revisedPrompt'),str):
            prompts['host_returned_revised_prompt']=prompt_value(doc('tool-result.json')['revisedPrompt'],
                'actual returned host metadata; distinct from request argument','tool-result.json/revisedPrompt')
        if not prompts['actual_submitted_prompt'] and not session:
            prompts['actual_submitted_prompt']=prompt_value(prepared,'archived recorded request used by generation workflow; no independent resolved-argument capture asserted','request.json') if prepared is not None else None
        recovery=doc('recovery-evidence.json')
        if recovery:
            cases['recovered_completion_evidence']+=1
            recovered_sha=recovery.get('source_sha256',recovery.get('sourceSha256'))
            if recovered_sha and recovered_sha!=generation.get('sha256'):errors.append({'slot':slot,'issue':'recovery source SHA mismatch'})
        raw=archive/'raw.png'; runtime=snap/'runtime'/slot
        raw_fact={'path':str(raw),'exists_at_capture':raw.is_file(),'recorded_sha256':generation.get('sha256'),
                  'recorded_native_size':[generation.get('width'),generation.get('height')]}
        if raw.is_file():
            with Image.open(raw) as im:raw_fact.update({'measured_native_size':[im.width,im.height],'measured_mode':im.mode,'measured_format':im.format})
            raw_fact['measured_sha256']=sha(raw)
            if raw_fact['measured_sha256']!=generation.get('sha256'):errors.append({'slot':slot,'issue':'raw SHA mismatch'})
            if raw_fact['measured_native_size']!=row.get('native_source_size'):errors.append({'slot':slot,'issue':'manifest native size mismatch'})
            if min(raw_fact['measured_native_size'])<1024:errors.append({'slot':slot,'issue':'native source smaller than1024'})
        else:missing.append({'slot':slot,'file':str(raw),'detail':'source pixels missing at evidence capture'})
        if generation.get('sha256')!=row.get('source_record',{}).get('source',{}).get('sha256'):
            errors.append({'slot':slot,'issue':'generation record versus processing source SHA mismatch'})
        source_hashes.append(generation.get('sha256'))
        if not runtime.is_file() or sha(runtime)!=row['sha256']:errors.append({'slot':slot,'issue':'runtime missing or SHA mismatch'})
        record_path=Path(row['source_record_file'])
        processing={'source_record':row.get('source_record'),'record_file':json_evidence(record_path) if record_path.is_file() else None}
        if not record_path.is_file():missing.append({'slot':slot,'file':str(record_path)})
        # Only explicit returned model/quality fields in the generation evidence may be normalized.
        actual_model=generation.get('actualModel'); actual_quality=generation.get('actualQuality')
        if actual_model in ('host-managed','host-managed-unverified','unverified','unknown'):actual_model=None
        if actual_quality in ('host-managed','host-managed-unverified','unverified','unknown'):actual_quality=None
        if actual_model is None:cases['actual_model_undisclosed']+=1
        if actual_quality is None:cases['actual_quality_undisclosed']+=1
        result.append({'slot':slot,'selected_revision':attempt,'runtime':{'path':str(runtime),'sha256':row['sha256'],'size':row['size']},
            'native_source':raw_fact,'documents':docs,'prompt_resolution':prompts,'processing':processing,
            'configuration_target_only':generation.get('configSnapshot',request.get('configSnapshot')),
            'submitted_parameters':request.get('submittedParameters',generation.get('submittedParameters')),
            'actualModel':actual_model,'actualQuality':actual_quality,
            'model_quality_evidence_limit':'Tool selectors/returned fields do not disclose a verifiable model or quality; prompt text and config targets never become actual parameters.' if actual_model is None or actual_quality is None else None,
            'timing':{'prepared_at_recorded':request.get('actual_request',{}).get('started_at',request.get('startedAt')),
                      'separate_submitted_at':submission.get('submitted_at'),
                      'completed_at_recorded':receipt.get('completed_at'),
                      'completed_at_basis':receipt.get('completed_at_basis'),
                      'host_completion_event_at':session.get('event_timestamp',recovery.get('timestamp')),
                      'generated_at_recorded':generation.get('generatedAt'),'generated_at_basis':generation.get('generatedAtBasis')},
            'formal_visual_approval_claimed_by_this_evidence':False,'client_integration_claimed':False})
    if len(set(source_hashes))!=136:errors.append({'issue':'selected source SHAs are missing or duplicated'})
    output={'schema':1,'character_id':CHAR,'captured_at':now(),'snapshot':str(snap),'manifest_sha256':sha(mp),
        'selection_input':json_evidence(selected_input) if selected_input.is_file() else None,
        'scope':'136 selected runtime slots and their untouched historical textual generation/source evidence',
        'source_records_modified':False,'image_files_modified':False,'raw_images_deleted_by_this_script':False,
        'count':len(result),'actual_walk':sum(x['slot'].startswith('walk/') for x in result),'actual_idle':sum(x['slot'].startswith('idle/') for x in result),
        'status':'captured_with_historical_limitations' if not missing and not errors else 'captured_with_evidence_gaps_or_errors',
        'case_counts':dict(cases),'missing_evidence':missing,'validation_errors':errors,'historical_limitations':limitations,
        'notes':['All source JSON exact UTF-8 text and SHA are retained alongside parsed content; no source document was rewritten.',
                 'Historical prompt exactActualRequestMatch claims remain visible in original documents; prompt_resolution records the actual contradictory evidence/errata.',
                 'A host revisedPrompt is returned metadata and is never promoted to directly captured resolved submission arguments.',
                 'A prepared request timestamp is not silently promoted to submission/completion time.',
                 'This file proves captured evidence, not artistic approval, browser playback, Unity or client integration.'],
        'files':result}
    save_new(destination,output)
    print(json.dumps({'output':str(destination),'sha256':sha(destination),'count':len(result),'missing_evidence':missing,
                     'validation_errors':errors,'case_counts':dict(cases),'historical_limitations_count':len(limitations)},ensure_ascii=False,indent=2))

if __name__=='__main__':main()

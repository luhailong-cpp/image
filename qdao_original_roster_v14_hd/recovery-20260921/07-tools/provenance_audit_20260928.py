"""Read-only source audit for character07; writes only a new audit report."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from PIL import Image, ImageOps

HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parent
OUT=HERE/'candidate/07_moon_shadow_assassin_girl'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(p): return str(p).replace('\\','/').lower()
def stamp(): return datetime.now(timezone.utc).isoformat()
def file_record(p): return {'path':str(p),'exists':p.is_file(),'sha256':sha(p) if p.is_file() else None}
def group_dupes(rows,key):
    groups=defaultdict(list)
    for r in rows:
        value=r.get(key)
        if value:groups[value].append(r['slot'])
    return [v for v in groups.values() if len(v)>1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=HERE/'provenance-audit-20260928.json');args=parser.parse_args()
    if args.out.exists():raise ValueError('New report required; refusing to overwrite existing audit')
    started=stamp();ledger=read(HERE/'cleanup-20260923.json');lookup={}
    def visit(v):
        if isinstance(v,dict):
            if v.get('path') and v.get('sha256'):lookup[(norm(v['path']),v['sha256'])]=v
            for x in v.values():visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    visit(ledger)
    rows=[];pixel_slots={};mirror_checks=[]
    for png in sorted(OUT.rglob('*.png')):
        side=Path(str(png)+'.generation.json');m=read(side);attempt=m['attempt'];folder=RECOVERY/'07-generation'/attempt
        request=folder/'request.json';prompt=folder/'prompt.txt';result=folder/'result.json'
        rq=read(request) if request.is_file() else {};rr=read(result) if result.is_file() else {}
        submitted=next((rq[k] for k in ('arguments','actual_request','submittedArguments') if isinstance(rq.get(k),dict)),{})
        text_prompt=prompt.read_text(encoding='utf-8-sig') if prompt.is_file() else None
        request_prompt=submitted.get('prompt');expected_source=m.get('derivedFrom',{}).get('sha256');source=Path(m.get('derivedFrom',{}).get('path',''))
        source_present=source.is_file();cleanup=lookup.get((norm(source),expected_source))
        archive=HERE/'archives'/attempt
        raw_record_path=Path(m.get('derivedFrom',{}).get('generationRecord',str(source)+'.generation.json'))
        raw_record=read(raw_record_path) if raw_record_path.is_file() else {}
        archived_receipt_path=archive/'generation-receipt.json';archived_receipt=read(archived_receipt_path) if archived_receipt_path.is_file() else {}
        refs=submitted.get('referenced_image_paths',[])
        model_values={'sidecar':[m.get('actualModel'),m.get('actualQuality')],'request':[rq.get('actualModel'),rq.get('actualQuality')],'result':[rr.get('actualModel'),rr.get('actualQuality')],'rawRecord':[raw_record.get('actualModel'),raw_record.get('actualQuality')]}
        result_payload=rr.get('tool_output') or rr.get('toolOutput') or rr
        hint=result_payload.get('output_hint','') if isinstance(result_payload,dict) else ''
        actual_returned=rr.get('original_generated_file') or rr.get('rawPath') or rr.get('raw_path')
        if not actual_returned:
            match=re.search(r'as (.+?\.png) by default',hint)
            if match:actual_returned=match.group(1)
        with Image.open(png) as im:
            final_size=list(im.size);final_mode=im.mode;alpha_range=list(im.getchannel('A').getextrema()) if im.mode=='RGBA' else None
            rgba=im.convert('RGBA');pixel_hash=hashlib.sha256(rgba.tobytes()).hexdigest();mirror_hash=hashlib.sha256(ImageOps.mirror(rgba).tobytes()).hexdigest()
        actual_source_sha=sha(source) if source_present else None
        if source_present:
            with Image.open(source) as im:
                native_size=list(im.size);native_mode=im.mode;native_alpha=list(im.getchannel('A').getextrema()) if im.mode=='RGBA' else None
        else:
            native_size=m.get('nativeMetrics',{}).get('size');native_mode=raw_record.get('mode') or archived_receipt.get('nativeMode');native_alpha=None
        raw_link_hash=raw_record.get('sha256') or archived_receipt.get('rawSha256')
        evidence={}
        for name,p in [('request',request),('result',result)]:
            binding=m.get(name+'Evidence') or raw_record.get(name+'Evidence') or {}
            evidence[name]={'recordedSha256':binding.get('sha256'),'currentShaMatchesRecorded':sha(p)==binding['sha256'] if p.is_file() and binding.get('sha256') else None}
        identities=[p for p in refs if 'portrait-inspection-1024.png' in norm(p) or '07_moon_shadow_assassin_girl_transparent_4096.png' in norm(p)]
        styles=[p for p in refs if norm(p).endswith('/designs/jubaozhai-ui/02-characters.png')]
        request_ref_bindings=rq.get('referenceBindings') or []
        refs_audit=[]
        for ref in refs:
            rpath=Path(ref)
            bindings=[b for b in request_ref_bindings if norm(b.get('path') or b.get('pathAtGeneration',''))==norm(ref)]
            if not bindings:
                bindings=[b for b in raw_record.get('references',[]) if norm(b.get('path',''))==norm(ref)]
            binding=bindings[0] if bindings else None
            current_sha=sha(rpath) if rpath.is_file() else None
            refs_audit.append({'path':ref,'submitted':True,'existsNow':rpath.is_file(),'currentSha256':current_sha,'generationTimeRecordedSha256':binding.get('sha256') if binding else None,'matchesGenerationTimeHash':current_sha==binding.get('sha256') if binding and current_sha else None,'note':'Editable pose references may now contain a later selected frame; immutable identity/style binding is checked separately.'})
        issues=[]
        if not all(p.is_file() for p in (request,prompt,result)):issues.append('missing_request_prompt_or_result')
        prompt_exact=text_prompt==request_prompt
        prompt_newline_equiv=text_prompt.rstrip('\r\n')==request_prompt.rstrip('\r\n') if isinstance(text_prompt,str) and isinstance(request_prompt,str) else False
        if not prompt_newline_equiv:issues.append('prompt_file_request_mismatch')
        if m.get('exactPrompt') and m['exactPrompt']!=request_prompt:issues.append('sidecar_request_prompt_mismatch')
        if sha(png)!=m.get('outputSha256'):issues.append('output_sha_mismatch')
        if final_size!=[1024,1024] or final_mode!='RGBA' or alpha_range!=[0,255]:issues.append('final_format_alpha_invalid')
        if source_present and actual_source_sha!=expected_source:issues.append('source_sha_mismatch')
        if not source_present and not (cleanup and cleanup.get('deletedAt')):issues.append('missing_source_without_completed_cleanup_record')
        if native_size is None or min(native_size)<1024 or native_mode!='RGBA':issues.append('native_minimum_or_mode_unproven')
        if raw_link_hash and raw_link_hash!=expected_source:issues.append('raw_record_sha_mismatch')
        if any(v['currentShaMatchesRecorded'] is False for v in evidence.values()):issues.append('request_result_evidence_hash_mismatch')
        if not actual_returned:issues.append('tool_return_path_unproven')
        if not identities:issues.append('original_identity_not_attached')
        if not styles:issues.append('approved_design_style_not_attached')
        if any(x for pair in model_values.values() for x in pair):issues.append('non_null_actual_model_or_quality_requires_evidence')
        factor=m.get('wholeCanvasScale')
        if factor is None or not 0<factor<=1:issues.append('native_downsample_not_proven')
        original_path=Path(actual_returned) if actual_returned else None
        original_match=sha(original_path)==expected_source if original_path and original_path.is_file() else None
        if original_match is False:issues.append('returned_original_source_sha_mismatch')
        if raw_record.get('resultEvidence',{}).get('sha256') and sha(result)!=raw_record['resultEvidence']['sha256']:issues.append('raw_receipt_result_binding_mismatch')
        row={'slot':m['slot'],'attempt':attempt,'snapshotAt':stamp(),'output':file_record(png),'sidecar':file_record(side),'outputSha256':sha(png),'finalSize':final_size,'finalMode':final_mode,'finalAlphaRange':alpha_range,'outputPixelSha256':pixel_hash,'mirroredPixelSha256':mirror_hash,'request':file_record(request),'prompt':file_record(prompt),'result':file_record(result),'promptExactlySameText':prompt_exact,'promptSameExceptTrailingNewlines':prompt_newline_equiv,'evidenceHashes':evidence,'source':str(source),'sourcePresent':source_present,'sourceSha256':expected_source,'currentSourceShaMatches':actual_source_sha==expected_source if source_present else None,'sourceEvidenceScope':'current_file' if source_present else 'record_only_after_authorized_cleanup','completedCleanupEntry':cleanup if not source_present else None,'nativeSize':native_size,'nativeMode':native_mode,'nativeAlphaRange':native_alpha,'sourceGenerationRecord':file_record(raw_record_path),'sourceGenerationRecordShaMatches':raw_link_hash==expected_source if raw_link_hash else None,'archivedReceipt':file_record(archived_receipt_path) if archived_receipt_path.is_file() else None,'actualReturnedPath':actual_returned,'returnedOriginalExists':original_path.is_file() if original_path else False,'returnedOriginalShaMatches':original_match,'identityActuallyAttached':identities,'approvedStyleActuallyAttached':styles,'referenceBindings':refs_audit,'modelQualityEvidence':model_values,'submittedParameters':rq.get('submittedParameters'),'operation':m.get('operation'),'wholeCanvasScale':factor,'paidApiCallEvidence':rr.get('paidApiCalls',rr.get('paid_api_calls')),'issues':issues}
        rows.append(row);pixel_slots[pixel_hash]=row['slot'];mirror_checks.append((row['slot'],mirror_hash))
    mirror_matches=[{'slot':slot,'exactMirroredPixelMatch':pixel_slots[h]} for slot,h in mirror_checks if h in pixel_slots]
    changed=[]
    for r in rows:
        p=Path(r['output']['path']);s=Path(r['sidecar']['path'])
        if sha(p)!=r['outputSha256'] or sha(s)!=r['sidecar']['sha256']:changed.append(r['slot'])
    summary={'slotCount':len(rows),'walkCount':sum(r['slot'].startswith('walk/') for r in rows),'idleCount':sum(r['slot'].startswith('idle/') for r in rows),'currentNativeSources':sum(r['sourcePresent'] for r in rows),'recordOnlySources':[r['slot'] for r in rows if not r['sourcePresent']],'missingRequestPromptResult':[r['slot'] for r in rows if 'missing_request_prompt_or_result' in r['issues']],'promptMismatch':[r['slot'] for r in rows if 'prompt_file_request_mismatch' in r['issues']],'missingIdentity':[r['slot'] for r in rows if not r['identityActuallyAttached']],'missingApprovedStyle':[r['slot'] for r in rows if not r['approvedStyleActuallyAttached']],'duplicateFinalByteSha':group_dupes(rows,'outputSha256'),'duplicateNativeSourceSha':group_dupes(rows,'sourceSha256'),'duplicateFinalPixelSha':group_dupes(rows,'outputPixelSha256'),'duplicateToolReturnPaths':group_dupes(rows,'actualReturnedPath'),'exactMirroredPixelMatches':mirror_matches,'changedDuringAudit':changed,'issueCounts':dict(Counter(issue for r in rows for issue in r['issues']))}
    summary['immutableReferencesWithoutGenerationTimeHash']=[{'slot':r['slot'],'path':b['path']} for r in rows for b in r['referenceBindings'] if b['path'] in r['identityActuallyAttached']+r['approvedStyleActuallyAttached'] and b['generationTimeRecordedSha256'] is None]
    summary['immutableReferencesGenerationTimeHashMismatch']=[{'slot':r['slot'],'path':b['path']} for r in rows for b in r['referenceBindings'] if b['path'] in r['identityActuallyAttached']+r['approvedStyleActuallyAttached'] and b['matchesGenerationTimeHash'] is False]
    summary['promptFileTerminalNewlineOnlyDifferenceCount']=sum(not r['promptExactlySameText'] and r['promptSameExceptTrailingNewlines'] for r in rows)
    report={'character':'07_moon_shadow_assassin_girl','startedAt':started,'completedAt':stamp(),'auditMode':'read_only_artwork_and_existing_provenance;new_report_only','snapshotNotFreeze':True,'summary':summary,'scopeLimitations':['Independent request, returned path and native/output hashes support distinct genuine tool outputs; they do not by themselves prove visible poses differ sufficiently. Visual gait acceptance is separate.','No exact byte/pixel duplicates and no exact horizontal mirrored pixel matches, when found clear, do not exclude semantically duplicate poses or transformations requiring visual analysis.','Historical deleted raw sources are record-only; no claim of current source pixel re-verification is made for them.','This audit checks recorded uniform downsample factors and native sizes; exact source-to-output pixel reconstruction is supplied by verify_candidates.py separately.','References pointing at editable current candidates can legitimately differ from the generation-time input; this report preserves both hashes and does not rewrite source records.','Some historical requests list the actual attached identity/style paths without a generation-time byte hash; their attachment parameter is proven, historical input bytes are not independently proven by this audit. Export-time bindings do not retroactively create generation-time evidence.','Actual model and quality remain unknown where the builtin tool did not disclose them. Configuration targets are not returned model evidence.'],'rows':rows}
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'report':str(args.out),'sha256':sha(args.out),'summary':summary},ensure_ascii=False))

if __name__=='__main__':main()

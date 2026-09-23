"""Read-only 32-patch provenance verification; unique reports are the only writes.

Limited compatibility: one exact style alias with a pinned SHA, lossless CRLF
to LF reconstruction of UTF-8 text, or an exact completed cleanup-log entry.
No art acceptance, generic missing-file bypass, or shared-state mutation.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, base64, hashlib, io, json, re
from PIL import Image

HERE=Path(__file__).resolve().parent
SESSION=HERE.parent
ART=SESSION.parents[1]
REPO=ART.parent
OLD_STYLE=REPO/'designs/guild-ui-v2/source/guild-overview.png'
NEW_STYLE=REPO/'designs/gameplay-ui/04-guild.png'
STYLE_SHA='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
OBSERVED={}
CHECKS=[]
ERRORS=[]
RETIRED={}

def digest(data):return hashlib.sha256(data).hexdigest()
def observe(path):
    path=Path(path).resolve();data=path.read_bytes();value=digest(data)
    if path in OBSERVED and OBSERVED[path]!=value:raise ValueError('Input changed between reads: '+str(path))
    OBSERVED.setdefault(path,value)
    return data
def read(path):return json.loads(observe(path).decode('utf-8-sig'))
def require(condition,message):
    if not condition:raise ValueError(message)
def resolve(value):
    path=Path(value)
    return path.resolve() if path.is_absolute() else (ART/path).resolve()

def check(path,expected=None,*,text=False,retired=False,pixels=None):
    path=resolve(path)
    result={'file':str(path),'expectedSha256':expected}
    data=None
    if path.is_file():
        data=observe(path);actual=digest(data)
        result.update(status='current_bytes_verified',sha256=actual)
        if expected and actual!=expected:
            require(text and path.suffix.lower() in ('.json','.jsonl','.txt','.md'), 'SHA mismatch: '+str(path))
            data.decode('utf-8-sig')
            normalized=data.replace(b'\r\n',b'\n')
            require(normalized!=data and digest(normalized)==expected,'SHA differs beyond exact CRLF-to-LF reconstruction: '+str(path))
            result.update(status='historical_lf_bytes_exactly_reconstructed',historicalLfSha256=expected,currentByteShaEqualsHistorical=False)
    elif path==OLD_STYLE.resolve():
        require(expected==STYLE_SHA,'Style alias must carry the exact pinned historical SHA')
        data=observe(NEW_STYLE)
        require(digest(data)==STYLE_SHA,'Canonical style bytes changed')
        result.update(status='same_bytes_at_exact_canonical_style_path',currentFile=str(NEW_STYLE),sha256=STYLE_SHA,historicalPathPresent=False)
    elif retired and path in RETIRED:
        require(expected and expected==RETIRED[path]['sha256'],'Missing source needs exact recorded pre-deletion SHA: '+str(path))
        result.update(status='historically_deleted_not_current_bytes_verified',cleanupLogLine=RETIRED[path]['line'],currentBytesVerified=False)
    else:raise FileNotFoundError('No current bytes or exact allowed evidence: '+str(path))
    if pixels is not None:
        require(data is not None,'Cannot decode deleted PNG')
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            require(image.format=='PNG' and list(image.size)==pixels,'PNG format or dimensions differ: '+str(path))
            require(image.mode!='RGBA' or image.getextrema()[3]==(255,255),'Unexpected transparency: '+str(path))
            result.update(pixels=list(image.size),mode=image.mode,fullPngDecode=True)
    CHECKS.append(result)
    return data

def image_path_from_receipt(receipt):
    hint=receipt.get('output_hint') or receipt.get('response',{}).get('output_hint')
    if hint:
        match=re.search(r' as (.+?\.png) by default\.',hint,re.S)
        require(match is not None,'Real receipt output_hint lacks saved file path')
        return resolve(match.group(1))
    return resolve(receipt['hostCompletion']['savedPath'])

def inspect_patch(tile,patch):
    native=Path(patch['native']) if patch.get('native') else tile/patch['outputFile']
    record_path=Path(patch['record']) if patch.get('record') else native.with_suffix('.record.json')
    record=read(record_path)
    native_sha=record.get('nativeSha256') or record.get('sha256')
    require(native_sha is not None,'Native record has no image SHA')
    require(resolve(record['file'])==native.resolve(),'Record file differs from selected native')
    require(record.get('actualModel') is None and record.get('actualQuality') is None and record.get('generatedAt') is None,'Unexpected verified model/quality/server time claim')
    require(record.get('submittedParameters')=={'model':None,'quality':None},'Unexpected submitted backend selector claims')
    require(not any(record.get(k) is True for k in ('accepted','formalAccepted','runtimePublished','upscaled','finalArtUpscaled','resampled','resizedAfterGeneration')),'Unexpected acceptance or resampling flag')
    require(record.get('configSnapshot',{}).get('model')=='gpt-image-2.5-sunburst' and record['configSnapshot'].get('quality')=='max','Batch target differs')
    native_bytes=check(native,native_sha,pixels=[1254,1254])
    if patch.get('sha256'):require(patch['sha256']==native_sha,'Plan selected native SHA mismatch')
    evidence=record['evidence']
    receipt_path=evidence.get('toolResponse') or evidence.get('file')
    receipt_bytes=check(receipt_path,evidence.get('sha256'),text=True)
    receipt=json.loads(receipt_bytes.decode('utf-8-sig'))
    if evidence.get('request'):
        request_bytes=check(evidence['request'],evidence['requestSha256'],text=True)
        request=json.loads(request_bytes.decode('utf-8-sig'))
        if receipt.get('request'):require(receipt['request']==request,'Record request differs from real receipt')
    else:
        require(isinstance(receipt.get('request'),dict),'Real receipt does not preserve actual request')
        request=receipt['request']
    prompt=check(record['promptFile'],record['promptSha256'],text=True)
    require(prompt.decode('utf-8-sig').replace('\r\n','\n')==request['prompt'].replace('\r\n','\n'),'Actual prompt differs from bound prompt text')
    references=record.get('references') or record.get('submittedImages')
    require(isinstance(references,list) and len(references)==len(request['referenced_image_paths']),'Actual request/reference count differs')
    for ref,actual in zip(references,request['referenced_image_paths']):
        refpath=ref.get('path') or ref.get('file')
        require(resolve(refpath)==resolve(actual),'Record path differs from actual submitted path')
        require(ref.get('sha256') is not None,'Reference SHA is missing')
        check(refpath,ref['sha256'],retired=True)
    output=resolve(record['toolOutputPath'])
    require(image_path_from_receipt(receipt)==output,'Real receipt source path differs from native record')
    require(record['toolOutputSha256']==native_sha,'Original output SHA differs from retained native')
    check(output,native_sha,retired=True)
    if receipt.get('recoveredFrom')=='archived_host_item_completed_event':
        revidence=receipt['evidence']
        raw=check(revidence['rawCompletionEvent'],revidence['rawCompletionEventSha256'],text=True)
        event=json.loads(raw)
        item=event['payload']['item']
        require(event['payload']['type']=='item_completed' and item['kind']=='image_gen.generation' and item['status']=='completed' and item['failure'] is None,'Invalid archived completion event')
        require(resolve(item['savedPath'])==output and item['revisedPrompt']==request['prompt'],'Archived completion is for a different source or request')
        require(base64.b64decode(item['result'])==native_bytes,'Archived returned image bytes differ')
        source=check(revidence['sourceSession'],revidence['sourceSessionSha256'],text=True)
        require(source.splitlines(keepends=True)[revidence['sourceSessionLineOneBased']-1]==raw,'Raw event is not the exact cited session line')
    if record.get('preflightEvidence'):
        p=record['preflightEvidence'];pre=read(Path(p['file']))
        check(p['file'],p['sha256'],text=True)
        require(pre.get('references')==[{'path':r.get('path') or r.get('file'),'sha256':r['sha256']} for r in references],'Before-submission reference hashes differ')
        if pre.get('requestSnapshot'):
            saved=check(pre['requestSnapshot'],pre['requestSha256'],text=True)
            require(json.loads(saved)==request,'Actual request differs from preflight request snapshot')
    return {'tile':tile.name.removeprefix('next_tile_'),'patch':patch['id'],'native':str(native),'sha256':native_sha,'record':str(record_path),'recordSha256':digest(observe(record_path)),'receipt':str(receipt_path),'actualRequestCompared':True,'status':'technical_links_consistent_not_art_accepted'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report-dir',type=Path,default=HERE/'verification')
    args=parser.parse_args();report_dir=args.report_dir.resolve()
    require(report_dir.is_relative_to(HERE),'Report must be in current continuation directory')
    cleanup=ART/'cleanup-current-assets';receipt=read(cleanup/'deletion-receipt.json')
    require(receipt.get('status')=='completed','Cleanup receipt incomplete')
    log=observe(cleanup/'deleted-files.jsonl').decode('utf-8-sig').splitlines()
    require(receipt['deletedFiles']==len(log),'Cleanup receipt count differs from exact log')
    for line,raw in enumerate(log,1):
        item=json.loads(raw);RETIRED[resolve(item['file'])]={'sha256':item['sha256'],'line':line}
    require(len(RETIRED)==len(log),'Duplicate cleanup path')
    results=[]
    for tileid in ('r08_c07','r08_c09'):
        tile=SESSION/('next_tile_'+tileid)
        plan=read(tile/'plan.json')
        require(len(plan['patches'])==16 and len({x['id'] for x in plan['patches']})==16,'Plan patch count invalid')
        for patch in plan['patches']:
            try:results.append(inspect_patch(tile,patch))
            except (OSError,ValueError,KeyError,TypeError,AssertionError) as error:ERRORS.append({'tile':tileid,'patch':patch['id'],'error':str(error)})
    changes=[]
    for path,before in OBSERVED.items():
        after=digest(path.read_bytes()) if path.is_file() else None
        if after!=before:changes.append({'file':str(path),'beforeSha256':before,'afterSha256':after})
    report={'schemaVersion':1,'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'STALE_FAIL' if changes else 'TECHNICAL_FAIL' if ERRORS else 'TECHNICAL_LINKS_CONSISTENT_WITH_EXPLICIT_HISTORY','scope':'Only 32 selected native patch records in c07/c09; not shared ledger, candidate art, semantic geometry, navigation, runtime, or formal acceptance','expectedPatchCount':32,'verifiedPatchCount':len(results),'errors':ERRORS,'changedInputs':changes,'checkCategories':dict(Counter(x['status'] for x in CHECKS)),'patches':results,'pointerChecks':CHECKS,'observedInputs':[{'file':str(p),'sha256':h} for p,h in OBSERVED.items()],'scriptSha256':digest(Path(__file__).read_bytes()),'artAcceptancePerformed':False,'formalAcceptancePerformed':False,'deletedInputsAreNotCurrentBytePasses':True}
    report_dir.mkdir(parents=True,exist_ok=True)
    destination=report_dir/('current-additions-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    with destination.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'report':str(destination),'status':report['status'],'verifiedPatchCount':len(results),'errors':ERRORS,'changes':changes,'checkCategories':report['checkCategories']},ensure_ascii=False))
    return 2 if ERRORS or changes else 0

if __name__=='__main__':raise SystemExit(main())

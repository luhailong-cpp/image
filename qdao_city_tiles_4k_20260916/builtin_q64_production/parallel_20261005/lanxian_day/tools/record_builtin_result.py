"""Save an actual builtin receipt and ingest native/guide output without inventing model evidence."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, shutil
from PIL import Image
from workflow import safe_output, sha256, read_json, write_json, ingest

def record(job_path, receipt_path, regional=False):
    job_path=Path(job_path).resolve(strict=True);receipt_path=Path(receipt_path).resolve(strict=True)
    job=read_json(job_path);receipt=read_json(receipt_path)
    source=Path(receipt['sourceOutputPath']).resolve(strict=True)
    prompt=receipt['prompt'];refs=receipt['references']
    job.update(sourceOutputPath=str(source),generatedAt=receipt['generatedAt'],prompt=prompt,
        references=refs,toolResultPath=str(receipt_path),expectedSha256=sha256(source))
    job['submittedParameters']={'model':None,'quality':None,'transparent_background':False,
        'prompt':prompt,'referenced_image_paths':[x['path'] for x in refs]}
    write_json(job_path,job)
    if not regional:
        return ingest(job_path)
    tile=safe_output(job['tileDir']);output=safe_output(tile/'regional/regional.png')
    if output.exists():raise FileExistsError(output)
    with Image.open(source) as im:
        if im.size!=(1254,1254) or im.format!='PNG':raise ValueError('Unexpected regional native size')
        size=list(im.size)
    shutil.copyfile(source,output)
    references=[]
    for ref in refs:
        p=Path(ref['path']).resolve(strict=True)
        with Image.open(p) as im:wh=list(im.size)
        references.append(dict(ref,path=str(p),sha256=sha256(p),pixels=wh))
    pf=safe_output(tile/'regional/regional.prompt.txt');pf.write_text(prompt,encoding='utf-8')
    result={'schemaVersion':1,'file':str(output),'sha256':sha256(output),'pixels':size,
        'generatedAt':receipt['generatedAt'],'ingestedAt':datetime.now(timezone.utc).isoformat(),
        'tool':'image_gen.imagegen','route':'builtin','configSnapshot':job['configSnapshot'],
        'submittedParameters':job['submittedParameters'],'actualModel':None,'actualQuality':None,
        'unverifiedReason':'Builtin exposes no model or quality selectors and result discloses neither.',
        'promptFile':str(pf),'promptSha256':sha256(pf),'references':references,
        'evidence':{'sourceOutputPath':str(source),'sourceOutputSha256':sha256(source),
            'toolResultPath':str(receipt_path),'toolResultSha256':sha256(receipt_path)},
        'role':'Regional structural guide only; never final 4096 pixels',
        'guideOnly':True,'finalArt':False,'formalAccepted':False}
    write_json(tile/'regional/generation.json',result)
    return {'image':str(output),'sha256':result['sha256']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job');p.add_argument('receipt');p.add_argument('--regional',action='store_true')
    a=p.parse_args();print(json.dumps(record(a.job,a.receipt,a.regional)))

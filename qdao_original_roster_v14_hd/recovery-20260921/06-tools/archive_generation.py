"""Archive an actual built-in image result; never invokes an API or invents model metadata.

prepare writes the exact request and frozen config before the image call. finalize
copies the actual output bytes and records returned evidence afterwards.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, importlib.util, json, shutil
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
IMAGE_ROOT=ROOT.parent
GEN=HERE.parent/'06-generation'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
def batch_path(name):
    import re
    assert re.fullmatch(r'[A-Za-z0-9_-]+',name)
    return GEN/name

def prepare(batch,prompt,references,reference_roles=None):
    folder=batch_path(batch)
    assert not folder.exists(), 'Use a fresh batch for every image invocation.'
    assert references and all(Path(p).is_file() for p in references)
    folder.mkdir(parents=True)
    request={'prompt':prompt,'referenced_image_paths':[str(Path(p).resolve()) for p in references]}
    (folder/'prompt.txt').write_bytes(prompt.encode('utf-8'))
    write(folder/'request.json',request)
    write(folder/'job.json',{'started_at':now(),'configSnapshot':read(IMAGE_ROOT/'config/image-generation.json'),
          'references':[{'path':p,'sha256':sha(p),'role':(reference_roles or {}).get(p,'reference as described in exact prompt')} for p in request['referenced_image_paths']],
          'request_sha256':sha(folder/'request.json'),'prompt_sha256':sha(folder/'prompt.txt')})
    return request

def finalize(batch,original,tool_result):
    folder=batch_path(batch);original=Path(original).resolve()
    assert original.is_file() and not (folder/'raw.png').exists()
    request,job=read(folder/'request.json'),read(folder/'job.json')
    assert sha(folder/'request.json')==job['request_sha256'] and sha(folder/'prompt.txt')==job['prompt_sha256']
    assert (folder/'prompt.txt').read_bytes().decode('utf-8')==request['prompt']
    shutil.copy2(original,folder/'raw.png')
    assert sha(original)==sha(folder/'raw.png')
    with Image.open(folder/'raw.png') as im:
        size=list(im.size);format_name=im.format;mode=im.mode
    assert format_name=='PNG' and min(size)>=1024, 'Actual native output does not meet the single-frame minimum.'
    completed=now()
    # Preserve the exact small result evidence supplied by the caller. Do not include base64 payloads.
    write(folder/'tool-result.json',tool_result)
    receipt={'schema':1,'tool':'built-in image_gen','route':'builtin','actual_model':'host-managed-unverified',
             'model_requested':'host-managed; no model selector','quality_requested':'host-managed; no quality selector',
             'actual_request':{**request,'started_at':job['started_at']},'submittedParameters':{'model':None,'quality':None},
             'actualModel':None,'actualQuality':None,'configSnapshot':job['configSnapshot'],
             'paid_api_calls':0,'generation_calls':1,'status':'generated_pending_review',
             'output_hint':tool_result.get('output_hint'),'original_generated_file':str(original),
             'completed_at':completed,'tool_result_file':'tool-result.json','tool_result_sha256':sha(folder/'tool-result.json')}
    write(folder/'generation-receipt.json',receipt)
    provenance={'path':str((folder/'raw.png').resolve()),'sha256':sha(folder/'raw.png'),'native_size':size,
                'mode':mode,'format':format_name,'original_generated_file':str(original),
                'original_matches_raw_sha256':True,'model_identity_verified':False,'signature_verified':False}
    write(folder/'provenance.json',provenance)
    record={'file':'raw.png','sha256':sha(folder/'raw.png'),'generatedAt':completed,'width':size[0],'height':size[1],
            'format':format_name,'tool':'built-in image_gen','route':'builtin','configSnapshot':job['configSnapshot'],
            'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,
            'evidence':[{'path':'generation-receipt.json','sha256':sha(folder/'generation-receipt.json')},
                        {'path':'tool-result.json','sha256':sha(folder/'tool-result.json')}],
            'unverifiedReason':'宿主管理，工具未披露实际型号或质量；配置目标和提示词不代表实际返回版本。',
            'prompt':'prompt.txt','prompt_sha256':sha(folder/'prompt.txt'),'references':job['references']}
    write(folder/'raw.png.generation.json',record)
    return {'archive':str(folder),'sha256':record['sha256'],'native_size':size,'actualModel':None,'actualQuality':None}

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('--batch',required=True);p.add_argument('--prompt-file',type=Path,required=True);p.add_argument('--reference',action='append',required=True)
    f=sub.add_parser('finalize');f.add_argument('--batch',required=True);f.add_argument('--original',type=Path,required=True);f.add_argument('--tool-result-json',type=Path,required=True)
    a=parser.parse_args()
    if a.command=='prepare': result=prepare(a.batch,a.prompt_file.read_bytes().decode('utf-8-sig'),a.reference)
    else: result=finalize(a.batch,a.original,read(a.tool_result_json))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

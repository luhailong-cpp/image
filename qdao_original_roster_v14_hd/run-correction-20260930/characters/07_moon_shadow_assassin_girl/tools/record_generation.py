"""Copy a native returned image and record evidence inside this character only."""
import argparse, hashlib, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
CONFIG=ROOT.parents[3]/'config/image-generation.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def record(source, relative, request, receipt):
    src=Path(source).resolve(); dst=(ROOT/'generation'/relative).resolve()
    dst.relative_to(ROOT/'generation')
    if dst.exists(): raise ValueError('Refusing to overwrite '+str(dst))
    req=json.loads(Path(request).read_text(encoding='utf-8-sig'))
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    with Image.open(dst) as im: dims=im.size; mode=im.mode; fmt=im.format
    text_path=dst.with_suffix('.tool-result.txt'); text_path.write_text(receipt,encoding='utf-8')
    prompt_path=dst.with_suffix('.prompt.txt')
    if not prompt_path.exists(): prompt_path.write_text(req['prompt'],encoding='utf-8')
    data={'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.now(timezone.utc).isoformat(),'generatedAtMeaning':'tool result received/copied timestamp','width':dims[0],'height':dims[1],'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(CONFIG.read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; model/quality selectors not exposed and result does not disclose actual values.','evidence':{'toolResult':str(text_path.relative_to(ROOT)),'sourceHostPath':str(src),'sourceHostSHA256':sha(src),'copiedSHAIdentical':sha(src)==sha(dst)},'prompt':str(prompt_path.relative_to(ROOT)),'references':[{'path':p,'sha256':sha(Path(p)),'role':'identity/camera reference' if 'designs/' not in p.replace('\\','/') else 'primary approved art style'} for p in req.get('referenced_image_paths',[])],'reviewStatus':'pending_static_and_dynamic_review','nativeHD':min(dims)>=1024,'operation':'verbatim copy of native tool output, no resampling'}
    dst.with_suffix(dst.suffix+'.generation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'file':str(dst),'sha256':data['sha256'],'size':dims,'mode':mode}))
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('source');p.add_argument('relative');p.add_argument('request');p.add_argument('--receipt',required=True);a=p.parse_args();record(a.source,a.relative,a.request,a.receipt)

"""Export only this agent's run W01-16; preserve full canvas."""
import json, hashlib, argparse, shutil, importlib.util
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

BASE=Path(__file__).resolve().parents[2]
ROOT=Path('D:/work/image')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser()
p.add_argument('--key',required=True)
p.add_argument('--source',required=True)
p.add_argument('--direction',required=True,choices=['W'])
p.add_argument('--frame',type=int,required=True)
p.add_argument('--review',required=True)
a=p.parse_args()
assert a.direction=='W' and 1<=a.frame<=16
source=Path(a.source)
assert source.is_file()
req=BASE/'provenance'/f'{a.key}.request.json'
args=json.loads(req.read_text(encoding='utf-8'))['args']
im=Image.open(source)
assert min(im.size)>=1024 and im.width==im.height and im.mode=='RGBA',(im.size,im.mode)
stage=BASE/'run/staging'/f'{a.key}.png'
stage.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,stage)
dest=BASE/'run'/a.direction/f'{a.frame:02}.png'
dest.parent.mkdir(parents=True,exist_ok=True)
if dest.exists():
    existing=json.loads(Path(str(dest)+'.generation.json').read_text(encoding='utf-8'))
    assert existing.get('prompt')==f'prompts/{a.key}.txt' or existing.get('review',{}).get('status','').startswith('rejected'),f'Refuse unrelated overwrite: {dest}'
spec=importlib.util.spec_from_file_location('export_frame', BASE/'tools/export_frame.py')
exporter=importlib.util.module_from_spec(spec); spec.loader.exec_module(exporter)
exporter.run(stage,dest)
export_record=json.loads(Path(str(dest)+'.generation.json').read_text(encoding='utf-8'))
receipt=BASE/'provenance'/f'{a.key}.receipt.json'
references=[]
for r in args.get('referenced_image_paths',[]):
    rp=Path(r)
    references.append({'path':rp.as_posix(),'sha256':sha(rp),'role':'Exact reference role in saved actual prompt'})
record={'file':dest.relative_to(BASE).as_posix(),'sha256':sha(dest),'generatedAt':datetime.now(timezone.utc).isoformat(),'generatedAtEvidence':'Local export observation, actual tool-generation timestamp unavailable','userTimezone':'America/New_York','width':1024,'height':1024,'format':'PNG','nativeSize':list(im.size),'nativeMode':im.mode,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**args},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool has no model/quality selectors and returned only image_url/output_hint. Actual model and quality unconfirmed.','evidence':{'request':req.relative_to(BASE).as_posix(),'receipt':receipt.relative_to(BASE).as_posix(),'receiptSHA256':sha(receipt)},'prompt':f'prompts/{a.key}.txt','references':references,'derivedFrom':{'path':stage.relative_to(BASE).as_posix(),'sha256':sha(stage),'hostOutputPath':source.as_posix(),'nativeSize':list(im.size),'available':True},'operation':{'type':'whole-canvas uniform downsample only','inputCanvas':list(im.size),'outputCanvas':[1024,1024],'scale':1024/im.width,'translation':[0,0],'boundingBoxNormalization':False,'lowestFootAlignment':False,'poseSynthesis':False},'anchor':{'fixedVirtualGroundY':942,'rootX':563,'method':'Prompted fixed camera/root; no per-frame pixel alignment','note':'Requires full-sequence visual check; generated pose may depart slightly from nominal prompt coordinates'},'review':{'status':'candidate-exported-awaiting-sequence-review','staticObservation':a.review,'clientIntegrated':False}}
record['operation']=export_record['operation']
raw_record={**record,'file':stage.relative_to(BASE).as_posix(),'sha256':sha(stage),'width':im.width,'height':im.height,'derivedFrom':None,'operation':{'type':'host_generated_native_output_copied_without_pixel_changes'},'hostOutputPath':source.as_posix()}
Path(str(stage)+'.generation.json').write_text(json.dumps(raw_record,ensure_ascii=False,indent=2),encoding='utf-8')
record['derivedFrom']['generationRecord']=Path(str(stage)+'.generation.json').relative_to(BASE).as_posix()
(Path(str(dest)+'.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
(BASE/'provenance'/f'{a.key}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':dest.as_posix(),'sha256':record['sha256'],'nativeSize':list(im.size),'bboxAlpha8':im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()}))

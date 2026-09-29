"""Bind complete PNG/APNG outputs to real native imagegen request evidence."""
from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]; O=R/'10-delivery-preview/current'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
m=read(O/'manifest.json');lm=read(O/'loops/manifest.json');rows=m['frames'];dirs=['N','NE','E','SE','S','SW','W','NW']
expected={d+f'{i:02}' for d in dirs for i in range(1,17)}|{d+'idle' for d in dirs}
assert set(rows)==expected and len(rows)==136
assert len(list((O/'walk').rglob('*.png')))==128 and len(list((O/'idle').glob('*.png')))==8
source_hashes=set();pixel_hashes=set();checks=[]
for slot,row in rows.items():
 target=O/row['file']; meta=read(Path(str(target)+'.generation.json')); raw=R/'10-generation'/row['archive']/'raw.png'; rawmeta=read(Path(str(raw)+'.generation.json'))
 assert sha(target)==row['sha256']==meta['sha256']
 assert sha(raw)==row['rawSHA256']==rawmeta['sha256'];assert row['rawSHA256'] not in source_hashes;source_hashes.add(row['rawSHA256'])
 im=Image.open(target);im.load();assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 pixel=hashlib.sha256(im.tobytes()).hexdigest();assert pixel==row['pixelSHA256'] and pixel not in pixel_hashes;pixel_hashes.add(pixel)
 assert min(rawmeta['width'],rawmeta['height'])>=1024
 ev=rawmeta['evidence'];req=read(ROOT/ev['request']);rec=read(ROOT/ev['receipt'])
 for field in ['request','toolResult','receipt']: assert sha(ROOT/ev[field])==ev[field+'SHA256']
 prompt=ROOT/rawmeta['prompt']['file'];assert sha(prompt)==rawmeta['prompt']['sha256']
 assert prompt.read_text(encoding='utf-8')==req['actual_request']['prompt']
 assert rawmeta['actualModel'] is None and rawmeta['actualQuality'] is None and rawmeta['unverifiedReason']
 assert req['actual_request']['referenced_image_paths'] and any('designs/' in p.replace('\\','/') for p in req['actual_request']['referenced_image_paths'])
 assert rec['paid_api_calls']==0
 # Reconstruct only the recorded delivery operation to verify lineage; not a new frame.
 native=Image.open(raw).convert('RGBA'); f=meta['operation']['factor']; resized=native.resize((round(native.width*f),round(native.height*f)),Image.Resampling.LANCZOS)
 expected_image=Image.new('RGBA',(1024,1024));expected_image.paste(resized,tuple(meta['operation']['translation']))
 assert expected_image.tobytes()==im.tobytes()
 checks.append({'slot':slot,'sha256':row['sha256'],'rawSHA256':row['rawSHA256'],'nativeSize':[rawmeta['width'],rawmeta['height']],'sourceEvidenceBound':True,'recordedExportPixelExact':True})
for d in dirs:
 p=O/lm[d]['file'];assert sha(p)==lm[d]['sha256'];loop=Image.open(p);assert loop.n_frames==16
 durations=[]
 for i in range(16):
  loop.seek(i);durations.append(loop.info['duration']);assert loop.convert('RGBA').tobytes()==Image.open(O/rows[d+f'{i+1:02}']['file']).convert('RGBA').tobytes()
 assert durations==[30]*16 and sum(durations)==480
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'character':'10_crimson_spear_girl','manifestSHA256':sha(O/'manifest.json'),'walkCount':128,'idleCount':8,'uniqueRawSources':136,'uniqueOutputPixels':136,'png1024Transparent':True,'nativeAtLeast1024':True,'eightLoops16Frames30ms480ms':True,'loopPixelsExactlySource':True,'sourceRequestReceiptPromptHashBound':True,'actualModel':None,'actualQuality':None,'visualAcceptance':'separate human/model visual review; not decided by this script','clientIntegration':'not_performed','files':checks}
(O/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))

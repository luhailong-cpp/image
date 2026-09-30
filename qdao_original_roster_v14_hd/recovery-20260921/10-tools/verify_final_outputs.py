"""Verify retained character-10 delivery after authorized source-image cleanup."""
from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json,hashlib,re
R=Path(__file__).resolve().parents[1]; ROOT=R.parents[1]; O=R/'10-delivery-preview/current'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(O/'manifest.json');a=read(O/'visual-acceptance.json');lm=read(O/'loops/manifest.json');v=read(O/'validation.json')
assert m['visualReview']=='accepted_offline' and a['status']=='accepted'
assert v['manifestSHA256']==sha(O/'manifest.json')
assert len(m['frames'])==136 and len(list((O/'walk').rglob('*.png')))==128 and len(list((O/'idle').glob('*.png')))==8
assert {x['slot']:x['sha256'] for x in a['files']}=={s:r['sha256'] for s,r in m['frames'].items()}
assert len({r['rawSHA256'] for r in m['frames'].values()})==136
pixels=set();source_text=0
for slot,row in m['frames'].items():
 p=O/row['file'];meta=read(Path(str(p)+'.generation.json'))
 assert sha(p)==row['sha256']==meta['sha256'] and meta['finalVisualReview']=='accepted'
 im=Image.open(p);im.load();assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 pixel=hashlib.sha256(im.tobytes()).hexdigest();assert pixel==row['pixelSHA256'] and pixel not in pixels;pixels.add(pixel)
 rawmeta=R/'10-generation'/row['archive']/'raw.png.generation.json'; rm=read(rawmeta)
 assert sha(rawmeta)==meta['derivedFrom'][0]['generationRecordSHA256']
 assert rm['sha256']==row['rawSHA256'] and min(rm['width'],rm['height'])>=1024
 for key in ['request','toolResult','receipt']:assert sha(ROOT/rm['evidence'][key])==rm['evidence'][key+'SHA256']
 assert sha(ROOT/rm['prompt']['file'])==rm['prompt']['sha256'];source_text+=1
for d in m['directions']:
 p=O/lm[d]['file'];assert sha(p)==lm[d]['sha256'];im=Image.open(p);assert im.n_frames==16
 for i in range(16):
  im.seek(i);assert im.info['duration']==30
  assert im.convert('RGBA').tobytes()==Image.open(O/m['frames'][d+f'{i+1:02}']['file']).convert('RGBA').tobytes()
 for bg in ['light','dark']:assert (O/'contact'/f'{d}-{bg}.jpg').is_file()
html=(O/'index.html').read_text(encoding='utf-8');embedded=json.loads(re.search(r'const M=(.*?);let playing=',html).group(1));assert embedded==m
report={'checkedAt':datetime.now(timezone.utc).isoformat(),'status':'passed','character':m['character'],'manifestSHA256':sha(O/'manifest.json'),'visualAcceptanceSHA256':sha(O/'visual-acceptance.json'),'walkCount':128,'idleCount':8,'loopCount':8,'frameDurationMs':30,'loopDurationMs':480,'retainedSourceTextRecordsVerified':source_text,'pixelsUnchanged':True,'previewReferencesComplete':True,'originalPixelsNeededForPlayback':False,'clientIntegration':'not_performed'}
(O/'post-cleanup-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,ensure_ascii=False))

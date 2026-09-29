"""Bind W/NW selected assets and generated review aids to exact SHA, no approval inference."""
from pathlib import Path
from PIL import Image
import hashlib,json
from datetime import datetime,timezone
import numpy as np
b=Path(__file__).resolve().parents[1]/'09-delivery-preview'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'character':'09_bamboo_archer_girl','recordedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'west_complete09','browserPlayback':'pending_root_review_subagent_CUA_no_browsers','clientIntegration':'not_performed','directions':{}}
for d,v in [('W',None),('NW','review20260928')]:
 w=b/'work'/d
 if v:w=w/'variants'/v
 records=[];sources=[];pixels=[];gifs=[]
 for rel in [f'walk/{d}/{f:02d}.png' for f in range(1,17)]+[f'idle/{d}.png']:
  p=w/'runtime'/rel;r=json.loads((w/'sources'/(rel+'.json')).read_text(encoding='utf-8'));im=Image.open(p)
  assert im.size==(1024,1024) and im.mode=='RGBA' and sha(p)==r['outputSha256']
  a=np.asarray(im)[:,:,3];assert min(a.flatten())==0 and max(a.flatten())==255
  assert not np.any(a[0]) and not np.any(a[-1]) and not np.any(a[:,0]) and not np.any(a[:,-1])
  assert abs(r['operation']['anchorAfterPx'][0]-512)<=.5 and r['operation']['anchorAfterPx'][1]==942
  raw=Path(r['source']['path']); assert sha(raw)==r['source']['sha256'] and min(Image.open(raw).size)>=1024
  records.append({'key':rel,'path':str(p),'sha256':sha(p),'rawSha256':sha(raw),'nativeSize':list(Image.open(raw).size),'anchor':r['operation']['anchorAfterPx'],'sourceRecordSha256':sha(w/'sources'/(rel+'.json'))})
  sources.append(sha(raw));pixels.append(hashlib.sha256(im.tobytes()).hexdigest())
 assert len(set(sources))==17 and len(set(pixels))==17
 for name in ['dark','light']:
  gp=w/'qa'/f'walk-30ms-{name}.gif';g=Image.open(gp);tim=[]
  for i in range(g.n_frames):g.seek(i);tim.append(g.info['duration'])
  assert len(tim)==16 and tim==[30]*16 and sum(tim)==480
  gifs.append({'path':str(gp),'sha256':sha(gp),'durationsMs':tim,'cycleMs':sum(tim)})
  idle=Image.open(w/'runtime'/'idle'/f'{d}.png').convert('RGBA');bg=(25,32,40,255) if name=='dark' else (242,239,225,255)
  c=Image.new('RGBA',idle.size,bg);c.alpha_composite(idle);c.convert('RGB').save(w/'qa'/f'idle-{name}-1024.png')
  for f in [8,14]:
   im=Image.open(w/'runtime'/'walk'/d/f'{f:02d}.png').convert('RGBA');c=Image.new('RGBA',im.size,bg);c.alpha_composite(im);c.convert('RGB').save(w/'qa'/f'full-{f:02d}-{name}-1024.png')
 report['directions'][d]={'selectedRoot':str(w),'walkCount':16,'independentIdleCount':1,'assets':records,'gifEvidence':gifs,'staticVisualReview':'pending_record_after_image_inspection'}
out=b/'west-static-evidence-20260928.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(out)

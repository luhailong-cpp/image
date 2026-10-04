from pathlib import Path
import json,hashlib,sys
import re,shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
B=Path(__file__).resolve().parents[1]
action=sys.argv[1]
if action=='save-batch':
 receipt=sys.argv[2]
 items=json.loads((B/receipt).read_text(encoding='utf-8'))
 cfg=json.loads((B.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
 for item in items:
  j=item['job']; hint=item['output_hint']
  source=re.search(r'as (C:\\[\s\S]*?\.png) by default',hint).group(1)
  p=B/j['dest']; p.parent.mkdir(parents=True,exist_ok=True)
  assert not p.exists(),p
  shutil.copyfile(source,p)
  im=Image.open(p);im.load()
  refs=[]
  for i,fp in enumerate(j['refs']):
   f=Path(fp);v=dict(path=fp,role='edit target / direction identity' if i==0 else ('approved painting style' if i==len(j['refs'])-1 else 'identity / phase reference'),sha256=hashlib.sha256(f.read_bytes()).hexdigest())
   if Path(str(f)+'.generation.json').exists():v['generationRecord']=str(f)+'.generation.json'
   refs.append(v)
  r=dict(file=j['dest'],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),generatedAt=datetime.now(ZoneInfo('America/New_York')).isoformat(),generatedAtMeaning='local receipt save time; server generation time undisclosed',width=im.width,height=im.height,format=im.format,mode=im.mode,tool='image_gen__imagegen',route='builtin',configSnapshot=cfg,submittedParameters=dict(model=None,quality=None,transparent_background=True,referenced_image_paths=j['refs']),actualModel=None,actualQuality=None,unverifiedReason='Host managed; no model/quality selector or returned evidence.',prompt=j['promptPath'],references=refs,editedFrom=refs[0],evidence=dict(receipt=receipt,output_path=source,entry=j['direction']+j['name']),review=dict(status='pending_visual_review',note='',dynamicAcceptance=False))
  Path(str(p)+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print('saved',j['direction'],j['name'],im.size,im.mode)
elif action=='enrich':
 name,d,receipt=sys.argv[2:]
 p=B/'generation/run'/d/(name+'.png.generation.json')
 r=json.loads(p.read_text(encoding='utf-8'))
 r['evidence']['receipt']=receipt
 for ref in r['references']:
  fp=Path(ref['path'])
  ref['sha256']=hashlib.sha256(fp.read_bytes()).hexdigest()
  gp=Path(str(fp)+'.generation.json')
  if gp.exists():ref['generationRecord']=str(gp)
 r['editedFrom']=r['references'][0]
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('enriched',d,name)
elif action=='selection':
 frames=[]
 for d in ['N','S']:
  for i in range(1,17):
   ps=list((B/'generation/run'/d).glob(f'{i:02d}-v*.png'))
   if not ps:continue
   p=max(ps,key=lambda p:int(p.stem.split('-v')[1]))
   gp=Path(str(p)+'.generation.json')
   r=json.loads(gp.read_text(encoding='utf-8'))
   assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
   frames.append(dict(action='run',direction=d,frame=i,source=p.relative_to(B).as_posix(),generationRecord=gp.relative_to(B).as_posix(),sha256=r['sha256'],width=r['width'],height=r['height'],status=r.get('review',{}).get('status','pending_visual_review'),visualReview=r.get('review',{}).get('note',''),dynamicReview='not_verified'))
 out=dict(schema=1,character='20_star_formation_master_girl',action='run',directions=['N','S'],frames=frames,dynamicAcceptance=False,timing=dict(status='trial_only',loopMs=[640,720,800],phaseTrial720Ms=[65,85,75,45,20,20,25,25]*2),note='每张新原生姿态由已提交旧方向图和本机新关键帧逐步定向编辑，旧步行未改名混入跑步。完整动态和客户端未通过。')
 (B/'run-NS-selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('selection frames',len(frames))


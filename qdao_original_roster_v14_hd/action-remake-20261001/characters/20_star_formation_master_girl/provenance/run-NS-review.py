from pathlib import Path
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
B=Path(__file__).resolve().parents[1]
selected={'N':[1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1], 'S':[2,1,2,3,2,2,2,2,2,1,3,2,4,3,2,2]}
notes=json.loads((B/'provenance/run-NS-static-notes.json').read_text(encoding='utf-8'))
frames=[]
now=datetime.now(ZoneInfo('America/New_York')).isoformat()
for d,versions in selected.items():
 for i,v in enumerate(versions,1):
  rel=f'generation/run/{d}/{i:02d}-v{v}.png'
  p=B/rel
  gp=Path(str(p)+'.generation.json')
  r=json.loads(gp.read_text(encoding='utf-8'))
  im=Image.open(p);im.load()
  sha=hashlib.sha256(p.read_bytes()).hexdigest()
  assert sha==r['sha256']
  assert im.mode=='RGBA' and min(im.size)>=1024
  assert im.getchannel('A').getextrema()==(0,255)
  assert r['actualModel'] is None and r['actualQuality'] is None
  for ref in r['references']:
   rf=Path(ref['path'])
   assert rf.is_file() and hashlib.sha256(rf.read_bytes()).hexdigest()==ref['sha256'],ref
  r['review']=dict(status='static_candidate',note=notes[d][i-1],reviewedAt=now,dynamicAcceptance=False,viewMethod='Actual generated image and full-frame contact sheet',bambooReferenceReview='Actual 09 runtime N/S contact sheets and selected single frames reviewed. S new ankle corrections attach actual bamboo runtime PNGs; N retained after comparison.')
  gp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  frames.append(dict(action='run',direction=d,frame=i,source=rel,generationRecord=gp.relative_to(B).as_posix(),sha256=sha,width=im.width,height=im.height,status='static_candidate',visualReview=notes[d][i-1],dynamicReview='not_verified'))
  for old in p.parent.glob(f'{i:02d}-v*.png.generation.json'):
   if old==gp: continue
   q=json.loads(old.read_text(encoding='utf-8'))
   reason='已由逐帧实看后更新候选替代，保留来源链文字。'
   if d=='S' and old.name=='04-v2.png.generation.json': reason='拒选：鞋底角度有所改善但误将屏右左支撑脚改成后折悬空，破坏相位。'
   if d=='S' and old.name=='13-v1.png.generation.json': reason='拒选：前摆腿出现裸膝/裸胫缺裤料，与全长象牙裤设计不符。'
   if d=='S' and i in [1,3,5,6,7,8,9,11,12,13,14,15,16] and not (i==13 and '-v1.' in old.name): reason='旧候选的前摆靴鞋底朝镜头面积偏大，后续附竹弓同向参考修踝俯仰；本图非当前选择。'
   q['review']=dict(status='superseded_or_rejected',note=reason,selectedReplacement=rel,dynamicAcceptance=False)
   old.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(frames)==32 and len({f['sha256'] for f in frames})==32
out=dict(schema=2,character='20_star_formation_master_girl',action='run',directions=['N','S'],frames=frames,selectedExplicitly=True,dynamicAcceptance=False,timing=dict(status='user_requested_preview_timing_not_dynamic_acceptance',loopMs=1200,frameMs=[75]*16,uniform=True),note='已审核本机旧walk但其固定肩肘不直接充作run；本机32帧采用方向身份与designs风格逐帧编辑，S附竹弓同向运行图修靴踝。所有静态候选仍需完整正常倍速动态验收。实际模型和质量未返回确认；客户端未接入。')
(B/'run-NS-selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
report=dict(selected=32,uniqueImages=32,nativeMode='RGBA',nativeSize=[1254,1254],alpha='0..255 each',referenceHashes='all selected references verified',timingMs=1200,dynamicAcceptance=False,checkedAt=now)
(B/'provenance/run-NS-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('32 selected RGBA native images and reference SHA verified')


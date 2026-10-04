from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[2]
p=B/'audit/archer-reference/nw-sw-selection.json'
old=json.loads(p.read_text(encoding='utf-8-sig'))
select={}
for di in ['NW','SW']:
 for n in [3,4,5,6,9,10,11,12,13,14]:
  select[f'run/{di}/{n:02}']=f'run-{di}-{n:02}-grounding-v1'
select.update({'run/NW/11':'run-NW-11-grounding-v3','run/SW/03':'run-SW-03-grounding-v2','run/SW/04':'run-SW-04-grounding-v2','run/SW/10':'run-SW-10-grounding-v2','run/SW/12':'run-SW-12-grounding-v3','run/SW/15':'run-SW-15-grounding-v2','run/SW/16':'run-SW-16-grounding-v1'})
out={**old,'schemaVersion':2,'scope':'NW/SW reviewed grounding candidates, runtime export by parent','updatedAt':datetime.now(timezone.utc).isoformat(),'userTiming':'同脚连续承重，支撑足相对身体沿行进轴逐段后移；每个位置两张独立姿态；16x75ms','dynamicPlaybackObserved':False,'rows':[]}
for r in old['rows']:
 rr=dict(r);slot=r['slot'];di=slot.split('/')[1];n=int(slot.split('/')[2])
 key=select.get(slot)
 if key:
  file=B/'sources/new'/f'{key}.png'
  assert file.exists(),file
  gen=B/'provenance/generation'/f'{key}.json';gj=json.loads(gen.read_text(encoding='utf-8-sig'))
  assert hashlib.sha256(file.read_bytes()).hexdigest()==gj['sha256']
  rr['supersededCandidate']={k:r.get(k) for k in ['candidateKey','file','sha256','generationRecord']}
  rr.update(candidateKey=key,file=file.as_posix(),sha256=gj['sha256'],generationRecord=gen.relative_to(B).as_posix(),export={'native':1254,'scaleCanvasTo':940,'offset':[42,49],'canvas':1024})
 side1=n in [15,16,1,2,3,4,5,6]
 rr['grounding']={'supportFoot':('left' if side1 else 'right') if di=='NW' else ('right' if side1 else 'left'),
   'pair': ('15-16' if n>=15 else f'{n if n%2 else n-1:02}-{n+1 if n%2 else n:02}'),
   'spatialStage':('前侧落地' if n in [15,16,7,8] else '身体接近支撑足' if n in [1,2,9,10] else '身过支撑足' if n in [3,4,11,12] else '后側推蹬'),
   'durationMs':75,'diagonalPlane':'SW前方左下较低、后方右上较高；NW前方左上较高、后方右下较低，不做最低像素贴地'}
 rr['staticCandidateReviewed']=True
 rr['staticReviewResult']='已查看原图及16格序列；候选可送父代理动态复审，未声称客户端验收'
 rr['clientIntegrated']=False
 out['rows'].append(rr)
assert len(out['rows'])==32
dst=B/'audit/archer-reference/nw-sw-grounding-selection.json'
dst.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(dst)


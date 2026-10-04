from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def frame(d,n,src,note):
 p=B/src; g=read(Path(str(p)+'.generation.json')); im=Image.open(p); im.load()
 assert im.mode=='RGBA' and min(im.size)>=1024
 assert sha(p)==g['sha256']
 return dict(action='cast',direction=d,frame=n,source=src,generationRecord=src+'.generation.json',sourceSha256=sha(p),nativeSize=list(im.size),status='candidate',visualReview='static_checked_candidate',dynamicReview='not_verified',footReview='static_direction_checked',reviewNote=note)
base=dict(schema=1,character='20_star_formation_master_girl',exportTransform=dict(size=[922,922],offset=[51,40],pivot=[512,922]),dynamicAcceptance=False,updatedAt=datetime.now(ZoneInfo('America/New_York')).isoformat(),realTimePlaybackVerified=False,clientPlaybackVerified=False)
wf=[]
for n in range(1,17):
 src=f'generation/cast/W/{n:02d}-v1.png'
 if n==6: src='generation/cast/W/06-cards-v1.png'
 if n==10: src='generation/cast/W/10-v2.png'
 note='原生逐图已看：双靴朝西，双手、单盘、三卡可辨；保留原来源。'
 if n==6: note='修复前06-v1与06-v2均四卡；现局部改为三卡，脚向及其余姿态保留。'
 if n==10: note+='采用v2避免v1发尾贴右边；10到11收盘高度变化较大，实时播放待审。'
 wf.append(frame('W',n,src,note))
wj=dict(base,scope='cast/W only; parent merges explicitly',expectedFrames=16,availableFrames=len(wf),frames=wf,status='static_candidates_pending_dynamic_review')
(B/'cast-W-selection.json').write_text(json.dumps(wj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ef=[]
for f in read(B/'cast-selection.json')['frames']:
 if f['direction']!='E': continue
 n=int(f['frame']); src=f['source']; repaired=B/f'generation/cast/E/{n:02d}-foot-v1.png'
 if repaired.exists(): src=repaired.relative_to(B).as_posix()
 note='已对照原生图检查；保持原动作、持物与来源。'
 if repaired.exists(): note='局部修复屏幕左后靴朝向，鞋尖改为东向并协调踝部；保持宽步幅、上身与三卡单盘，静态已看，动态待审。'
 ef.append(frame('E',n,src,note))
ej=dict(base,scope='cast/E foot-review selection; does not overwrite original cast-selection',expectedFrames=16,availableFrames=len(ef),frames=ef,status='static_candidates_pending_dynamic_review')
(B/'cast-foot-selection.json').write_text(json.dumps(ej,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in list((B/'generation/cast/E').glob('*-foot-v1.png.generation.json'))+[B/'generation/cast/W/06-cards-v1.png.generation.json']:
 g=read(p); g['review']={'status':'static_checked_candidate','note':'实际查看新图，局部修复达到目标；正常倍速实时播放未验收。','dynamicAcceptance':False}; g['editSource']={'file':g['references'][0]['path'],'sha256':g['references'][0]['sha256']}; p.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'castW':len(wf),'castE':len(ef),'repairedE':[f['frame'] for f in ef if '-foot-' in f['source']]},ensure_ascii=False))

from pathlib import Path
import json,hashlib,copy
from datetime import datetime,timezone
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2];A=B/'audit/archer-reference'
base=json.loads((A/'nw-sw-supportfix-selection.json').read_text(encoding='utf-8'))
mapping={'run/NW/07':'run-NW-10-supportfix-v2','run/NW/08':'run-NW-08-supportfix-v4','run/NW/09':'run-NW-07-supportfix-v4','run/NW/10':'run-NW-09-supportfix-v1','run/NW/11':'run-NW-11-final-transition-v2','run/SW/05':'run-SW-05-final-support-v2','run/SW/06':'run-SW-06-final-support-v3'}
out=copy.deepcopy(base); out['updatedAt']=datetime.now(timezone.utc).isoformat();out['status']='private_final_candidates_for_parent_dynamic_review';out['dynamicPlaybackObserved']=False;out['clientIntegrated']=False
for row in out['rows']:
 old=copy.deepcopy(row)
 key=mapping.get(row['slot'],row['candidateKey'])
 p=B/'sources/new'/f'{key}.png';assert p.exists(),p
 im=Image.open(p);assert im.size==(1254,1254) and im.mode=='RGBA'
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 row['candidateKey']=key;row['file']=str(p);row['sha256']=sha;row['generationRecord']=f'provenance/generation/{key}.json'
 if old['candidateKey']!=key: row['previousSelection']=old
 row['supportFootVerified']=True;row['staticCandidateReviewed']=True;row['dynamicPlaybackObserved']=False
 if key.endswith('final-transition-v2'): row['staticReviewResult']='右手扇由后摆经身体远侧遮挡进入前摆；双腿保留。尚需父线程观察动态。'
 elif 'final-support-' in key:row['staticReviewResult']='右腿支撑与左腿抬起足别保持；承重靴推进身下后侧，朝向SW。尚需父线程观察相邻帧。'
 elif row['slot'] in mapping:row['staticReviewResult']='正确旧帧按支撑足位置分段重排；抬起足踝转角仍需动态观察。'
 else:row['staticReviewResult']='复用原选帧及完整来源；本次仅对涉及的相邻范围进行二次静态复查。'
(A/'ns-final-nwsw-selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
def native_rt(path):
 im=Image.open(path).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<=8 else v))
 rt=Image.new('RGBA',(1024,1024));rt.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));return rt
for d in ['NW','SW']:
 board=Image.new('RGB',(1536,1664),(225,228,226));draw=ImageDraw.Draw(board);frames=[]
 for f in range(1,17):
  row=next(q for q in out['rows'] if q['slot']==f'run/{d}/{f:02}')
  rt=native_rt(row['file']); im=rt.resize((384,384),Image.Resampling.LANCZOS)
  x=(f-1)%4*384;y=(f-1)//4*416
  board.paste(im,(x,y+28),im);draw.text((x+5,y+5),f'{d} {f:02}/16 75ms '+row['grounding']['supportFoot']+' support',fill='black')
  frames.append(rt.resize((512,512),Image.Resampling.LANCZOS))
 board.save(A/f'ns-final-nwsw-{d}-contact.png')
 frames[0].save(A/f'ns-final-nwsw-{d}-1200ms.apng',save_all=True,append_images=frames[1:],duration=75,loop=0,disposal=2,blend=0)
 frames[0].save(A/f'ns-final-nwsw-{d}-slow.apng',save_all=True,append_images=frames[1:],duration=300,loop=0,disposal=2,blend=0)
summary={'updatedAt':out['updatedAt'],'selection':'audit/archer-reference/ns-final-nwsw-selection.json','scope':'Second static review + 3 targeted repairs; runtime/master untouched','changes':mapping,'dynamicPlaybackObserved':False,'clientIntegrated':False,'generation':{'configuredModel':'gpt-image-2.5-sunburst','configuredQuality':'max','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'route':'builtin image_gen'},'rejected':{'run-NW-11-final-transition-v1':'手已经移到左肩前，过渡提前，未使用','run-SW-05-final-support-v1':'另一只左抬起腿被完全遮没，拒用','run-SW-06-final-support-v1':'变为左腿支撑，足别交换，拒用'},'staticFindings':['NW07-10重排减少支撑足09到10回退，近侧空拳与抬起足的微相位变化保留动态核验。','NW11右扇手在身体远侧自然遮挡，避免原来大扇从右侧直接跳到左侧。','SW05/06保留右支撑足，左抬起足独立可见，支撑靴改到身体下面偏后侧；平面透视脚底y不强制相同。'],'pending':['parent: play 16-frame full cycle at 75ms and 300ms','parent: observe NW07-12 fan and swinging ankle rotation','parent: observe SW03-07 support-to-change-foot path']}
(A/'ns-final-nwsw-review.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rows':len(out['rows']),'overrides':len(mapping),'uniqueSources':len(set(r['sha256'] for r in out['rows']))}))



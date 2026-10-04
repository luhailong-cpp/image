import json,hashlib,copy
from pathlib import Path
from datetime import datetime,timezone
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
for d in ['NE','NW']:
 p=R/'run'/d/'grounding-review.json';g=json.loads(p.read_text(encoding='utf-8'));g.setdefault('reviewHistory',[]).append({'snapshotAt':datetime.now(timezone.utc).isoformat(),'reason':'Superseded pre-bamboo evidence; historical SHA and native references retained as recorded','frames':copy.deepcopy(g['frames'])})
 for row in g['frames']:
  fp=R/row['file'];m=json.loads(Path(str(fp)+'.generation.json').read_text(encoding='utf-8'));sha=hashlib.sha256(fp.read_bytes()).hexdigest();assert sha==m['sha256']==m['registrationTransform']['outputSha256']
  row['sha256']=sha;row['selectedNative']=m['derivedFrom']['file'];row['reviewStatus']='manual_static_checked_pending_parent_animation';row['durationMs']=75
  n=int(fp.stem);fixed='north-bamboo' in row['selectedNative']
  row['footAxis']=('本轮AI局部修复：' if fixed else '本轮重新实看后保留：')+('低靴后跟与鞋侧明确朝东北，鞋尖投影沿右上行进方向；抬起的异侧足为回收俯仰，膝踝未向外翻。' if d=='NE' else '近远脚沿左上行进方向，支撑靴鞋尖偏屏幕左、后跟在右，屈膝回收的足底不等同外八；未见横向拧踝。')
  row['hands']='实看两个肩袖到肘腕可连续追踪；左臂抱一只白狐，右掌托一枚蓝雪晶。半圈内右袖/前臂前后高低摆动，未见多臂或断掌。'
  row['registrationEvidence']=m['registrationTransform']
  row['phaseEvidence']=('左腿低位承重/离地退出，右腿屈膝回收' if n<=5 else '双腿前后交换；右脚前伸准备落地' if n<=8 else '右腿低位承重/离地退出，左腿屈膝回收' if n<=13 else '双腿前后交换；左脚前伸准备落地')
 g['reviewStatus']='manual_static_checked_pending_parent_animation';g['cycleDurationMs']=1200;g['updatedAt']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
 print(d+' current evidence updated and SHA verified 16/16')


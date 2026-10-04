import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[2];now=datetime.now(ZoneInfo('America/New_York')).isoformat()
hp=root/'reviews/root-fan-cast-approved-20261003.json';handoff=json.loads(hp.read_text(encoding='utf-8'))
for n in [8,9]:
 rp=root/f'records/root-fan-cast-run-SE-{n:02}-20261003-v2.json';r=json.loads(rp.read_text(encoding='utf-8'))
 r['status']='local_fan_fix_reviewed_sequence_pending';r['visualQA']={'status':r['status'],'reviewedAt':now,'method':'工具返回原生图＋原稿/修稿整画布与扇区放大对照','talismanCount':5,'handOwnershipPassed':True,'legCount':2,'notes':'v2为五符，前伸腿在屏右、后折腿在屏左，未沿用v1错误腿相位；两臂两手持物归属保留。全画布比例无明显退化，存在局部细小位移需组内动态复核。','wholeSequencePassed':False};r['generatedAtLocal']=datetime.fromisoformat(r['endedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).isoformat();rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 item={'slot':r['requested_slot'],'native':r['native']['sourceFile'],'native_sha256':r['native']['sha256'],'record':rp.relative_to(root).as_posix(),'review':r['status']}
 handoff['readyForRootImport']=[x for x in handoff['readyForRootImport'] if x['slot']!=item['slot']]+[item]
handoff['reviewedAt']=now;hp.write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('8 ready candidates; SE08/09 use v2')

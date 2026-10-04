import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
root=Path(__file__).resolve().parents[2]
accepted=[];rejected=[];now=datetime.now(ZoneInfo('America/New_York')).isoformat()
for rp in sorted((root/'records').glob('root-fan-cast-*-20261003-v1.json')):
 r=json.loads(rp.read_text(encoding='utf-8-sig'));slot=r['requested_slot'];reject=slot in ['run/SE/08','run/SE/09']
 qa={'reviewedAt':now,'method':'真实原生图工具返回及原稿/修稿整画布对照、符扇局部放大人工目视','talismanCount':5,'handOwnershipPassed':True,'status':'rejected_pose_change' if reject else 'local_fan_fix_reviewed_sequence_pending','notes':'虽然五符，但腿部相位被SE01参考带偏；SE08还有额外后鞋轮廓。不得导出。' if reject else '六符已改五符；持手归属、原姿态、鞋轴和全画布构图未见明显退化。局部重画有细小像素变化，仍需组内动态复核。','wholeSequencePassed':False}
 r['visualQA']=qa;r['status']=qa['status'];r['generatedAtLocal']=datetime.fromisoformat(r['endedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).isoformat();rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 item={'slot':slot,'native':r['native']['sourceFile'],'native_sha256':r['native']['sha256'],'record':rp.relative_to(root).as_posix(),'review':qa['status']}
 (rejected if reject else accepted).append(item)
(root/'reviews/root-fan-cast-approved-20261003.json').write_text(json.dumps({'reviewedAt':now,'readyForRootImport':accepted,'rejectedDoNotImport':rejected,'formalFilesChanged':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('ready',len(accepted),'rejected',len(rejected))

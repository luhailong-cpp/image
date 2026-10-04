import json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'inventory-cast.json';inv=json.loads(p.read_text(encoding='utf-8'))
reason='独立复审确认E06-12胸襟正面展开时，近右肩接到屏左铃臂、远左肩接到屏右符臂，归属反转；撤销此前归属通过，需重画肩袖-肘腕链。脚向复查结论仍单独保留。'
for f in inv['frames']:
 if f['direction']=='E' and (6<=f['frame']<=12 or f['frame']==14):
  f['visual_status']='needs_hand_ownership_repair';rp=root/f['source_record'];r=json.loads(rp.read_text(encoding='utf-8-sig'));r['visualQA'].update(status='needs_hand_ownership_repair',handOwnershipPassed=False,correction=reason);rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inv['qa_summary']['knownHandOwnershipFailures']=['E'+str(n).zfill(2) for n in list(range(6,13))+[14]];p.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qp=root/'records/cast-qa-20261003.json';q=json.loads(qp.read_text(encoding='utf-8'));q['handOwnershipCorrection']=reason;q['knownHandOwnershipFailures']=inv['qa_summary']['knownHandOwnershipFailures']
for f in q['frames']:
 if f['direction']=='E' and (6<=f['frame']<=12 or f['frame']==14):f['status']='needs_hand_ownership_repair';f['findings']=reason if f['frame']!=14 else 'E14三袖：近右肩空袖、后铃袖、胸右符腕小袖；需修成总共两臂两袖，近右符远左铃。'
qp.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Retracted E06-12 ownership pass; frame pixels unchanged')

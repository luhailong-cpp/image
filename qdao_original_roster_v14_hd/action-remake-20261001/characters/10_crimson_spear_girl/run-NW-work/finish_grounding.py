from pathlib import Path
import json,hashlib
d=Path(__file__).parent
sel=json.loads((d/'selection.json').read_text());sel['slots']['run/NW/09']='run-NW-work/run-NW-09-v3.png';sel['status']='static_sequence_reviewed_dynamic_pending';sel['latestRepair']='Slot09 heel-roll/toe-push edit reviewed against09 accepted reference; other15 retained'
(d/'selection.json').write_text(json.dumps(sel,ensure_ascii=False,indent=2),encoding='utf8')
t=json.loads((d/'timing-grounding.json').read_text(encoding='utf8'))
for f in t.get('frames',[]):
 if f['slot']==9:f.update({'file':'run-NW-09-v3.png','sha256':hashlib.sha256((d/'run-NW-09-v3.png').read_bytes()).hexdigest(),'phase':'A forefoot push / raised heel','durationMs':75})
for f in t.get('phases',[]):
 if f['slot']==9:f['phase']='A forefoot push / raised heel'
t['staticReview']='All16 full images and feet contact sheet reviewed. A06-09 to B13-16 support alternates. 07v2/15v2 compression,08v2 passing.09v3 now shows raised heel and forefoot push before compact10 exchange. All16 use uniform75ms;1200ms loop. Dynamic/client validation pending.'
(d/'timing-grounding.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
p=d/'REVIEW_20261003.md';s=p.read_text(encoding='utf8').replace('08-v2, 09-v2,','08-v2, 09-v3,')
s=s.replace('09-v2仍偏后期支撑，不能硬称前掌已充分蹬起；下一槽10出现紧凑腾空交换，动态连接由根窗口复看。','原09-v2后期支撑仍偏平掌，现槽09替换为09-v3：同A腿前掌继续发力，脚跟明显抬起、鞋底后部可见；下一槽10进入紧凑腾空交换。没有提前换承重腿。动态连接仍由根窗口复看。')
s+='\n\n参照09当前版的W/NW/SW同方向正式runtime已只读审阅，差异详见 ../run-SW-first-work/09_REFERENCE_COMPARISON_20261003.md。09-v3仅修原槽09踝部蹬离，保持脚长轴朝左上、同腿链及原高低双手握枪，其他15张保留。实际新来源SHA为879237626433d4e64ecf602cfda849c2a93ca55a015448553eb7a46d58754777，工具model/quality仍null。\n'
p.write_text(s,encoding='utf8')
for key,relative in sel['slots'].items():
 p=d.parent/relative;meta=p.with_name(p.name+'.generation.json');m=json.loads(meta.read_text(encoding='utf8'));m['visualReview']={'status':'static-reviewed','selectedSlot':key,'document':'REVIEW_20261003.md','dynamicValidation':False};meta.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('NW09 updated, all16 metadata static-review linked')


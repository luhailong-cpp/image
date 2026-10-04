from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
chosen={'E':{3:(3,'candidate','单眼右向峰值，膝髋降低及向左后仰明确，固定双靴轮廓。')},'W':{4:(4,'candidate','03-v4生成结果更接近回弹相位，按实图选为04；不重复占用03槽。')}}
for d,entries in chosen.items():
 p=ROOT/('hit-selection.json' if d=='E' else 'hit-W-selection.json');sel=json.loads(p.read_text(encoding='utf-8-sig'))
 for f,(v,status,note) in entries.items():
  original_slot=3
  src=f'generation/hit/{d}/{original_slot:02d}-v{v}.png';rp=ROOT/(src+'.generation.json');r=json.loads(rp.read_text(encoding='utf-8-sig'))
  r['review']={'status':status,'note':note,'dynamicAcceptance':False};rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  new={'action':'hit','direction':d,'frame':f,'source':src,'generationRecord':src+'.generation.json','sourceSha256':r['sha256'],'status':status,'visualReview':'static_checked_candidate','sequenceNote':note,'dynamicReview':'not_verified'}
  sel['frames']=[x for x in sel['frames'] if x['frame']!=f]+[new]
 sel['frames'].sort(key=lambda x:x['frame']);sel['dynamicAcceptance']=False;sel['updatedAt']=datetime.now(ZoneInfo('America/New_York')).isoformat()
 p.write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rejects={'E/03-v2':'远侧第二只眼，已由03-v3修复。','W/03-v3':'峰值骨架有改善但右侧发梢触边，需修边界。','W/03-v5':'修发时整体画幅自动放大/平移，盘侧触边，不进入选帧。'}
for k,note in rejects.items():
 p=ROOT/f'generation/hit/{k}.png.generation.json';r=json.loads(p.read_text(encoding='utf-8-sig'));r['review']={'status':'rejected','note':note,'dynamicAcceptance':False};p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('updated candidate selection and rejected attempts')

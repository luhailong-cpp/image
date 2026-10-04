import json
from pathlib import Path
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
for b in [8,9,10]:
 p=R/'provenance'/f'north-bamboo-ground2-batch{b}-receipts.json'
 rows=json.loads(p.read_text(encoding='utf-8'))
 for rc in rows:
  rc['path']=rc['hint'].split(' as ')[1].split(' by default.')[0]
  tp=R/'provenance'/(rc['q']['id']+'.tool-result.json')
  data=json.loads(tp.read_text(encoding='utf-8')); data['result'].pop('image_url',None); data['result']['imageSavedPath']=rc['path'];tp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')


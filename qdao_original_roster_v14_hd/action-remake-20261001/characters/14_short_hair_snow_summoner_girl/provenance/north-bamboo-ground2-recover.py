import json
from pathlib import Path
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
H=Path(r'C:/Users/luyua/.codex/generated_images/01a100fd-d4d0-7de2-9cd6-fbc6056ccb06')
maps={5:[('NE','07','v1','688d763a-6e5c-4c0b-ad07-eea81c174072',True),('NE','08','v1','23513f8c-0be7-4777-9b21-61f62dd360f4',False),('NE','09','v1','21f2f136-9a9d-4d10-ba4e-ffca0bfca769',False),('NE','10','v1','705e1a3d-c2dc-49df-ae37-8c743828b675',False)],6:[('N','08','v3','e7323ea7-465f-4eeb-b6a3-6a8de9c2b5d7',True),('N','10','v3','bd102344-a437-4557-aa03-1e30df54e259',True)],7:[('NE','13','v1','6e463b0e-f419-4c49-a94b-e32564184473',True),('NE','14','v1','8a0ba3aa-13ce-4621-87e2-dcbf69f1a848',False),('NE','15','v1','26554231-dfa9-43e9-950f-ffed42438907',False),('NE','16','v1','856c8817-6158-485f-bf25-8bc386b6b5c7',False)]}
for batch,entries in maps.items():
 rows=[]
 for d,f,v,u,explicit in entries:
  q=json.loads((R/'provenance'/f'north-bamboo-ground2-{d}-{f}-{v}.request.json').read_text(encoding='utf-8'));p=H/('exec-'+u+'.png');assert p.exists()
  hint=('Returned host path recorded in conversation before environment reload.' if explicit else 'INFERRED mapping after environment reload: isolated batch native file chronology and visually matched unchanged upper body. Full result object was lost; not tool-confirmed association.')
  rows.append({'q':q,'path':str(p),'hint':hint,'recoveryEvidence':{'association': 'conversation_tool_path' if explicit else 'inferred_from_chronology_and_visual_identity','actualModel':None,'actualQuality':None}})
 (R/'provenance'/f'north-bamboo-ground2-batch{batch}-receipts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Recovered batch5/6/7 textual evidence; six NE mappings explicitly marked inferred')

import json,hashlib
from pathlib import Path
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
rows=[]
for b in [5,7]:
 for rc in json.loads((R/'provenance'/f'north-bamboo-ground2-batch{b}-receipts.json').read_text(encoding='utf-8')):
  print(rc['q']['id'], {k:v for k,v in rc.items() if k not in ['q','hint']})


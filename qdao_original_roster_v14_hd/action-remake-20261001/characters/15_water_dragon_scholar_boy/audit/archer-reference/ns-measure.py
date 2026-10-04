from pathlib import Path
import json
from PIL import Image
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy')
rows=json.loads((B/'audit/archer-reference/ns-current-native.json').read_text())
for d in ['N','S']:
 print(d+' current')
 for r in rows:
  if r['direction']==d:
   a=Image.open(r['path']).getchannel('A');bb=a.point(lambda v:255 if v>8 else 0).getbbox()
   print(r['frame'],bb)
 print(d+' new')
 for p in sorted((B/'sources/new').glob('run-'+d+'-*-ground*.png')):
  a=Image.open(p).getchannel('A');bb=a.point(lambda v:255 if v>8 else 0).getbbox()
  print(p.stem,bb)


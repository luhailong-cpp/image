import json,shutil
from pathlib import Path
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
gr=json.loads((R/'run/staging/run-N-01-v1.png.generation.json').read_text(encoding='utf-8'))
shutil.copy2(gr['evidence']['toolReturnedPath'],R/'run/staging/north-bamboo-source-N-01.png')
print(gr['evidence']['toolReturnedPath'])


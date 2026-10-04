from pathlib import Path
from PIL import Image
import json
d=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl/attack-W-grounding-work')
for n in ['04-ground-v3','05-ground-v1','06-ground-v4','07-ground-v2','08-ground-v2']:
 p=d/f'attack-W-{n}.png';a=Image.open(p).getchannel('A');b=a.point(lambda x:255 if x>32 else 0).getbbox()
 edges=[a.crop(r).getextrema()[1] for r in [(0,0,1,1254),(1253,0,1254,1254),(0,0,1254,1),(0,1253,1254,1254)]]
 print(n,b,edges)


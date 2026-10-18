from pathlib import Path
import json,hashlib
from PIL import Image
Z=Path(__file__).resolve().parents[1]
out=Z/'qa/r03_c01_first2_quickcheck_20261016';out.mkdir(exist_ok=True)
neighbor=Image.open(Z/'tiles/r03_c02_candidate-v7_4096.png').convert('RGB')
for row in [1,4]:
 stem=f'r03_c01_s{row:02d}_04_a01'
 a=Image.open(Z/'native'/f'{stem}.png').convert('RGB')
 b=Image.new('RGB',(700,1024));b.paste(a.crop((789,115,1139,1139)),(0,0));b.paste(neighbor.crop((0,(row-1)*1024,350,row*1024)),(350,0))
 p=out/f'{stem}_right_pair.png'
 if not p.exists():b.save(p)
 print(p)

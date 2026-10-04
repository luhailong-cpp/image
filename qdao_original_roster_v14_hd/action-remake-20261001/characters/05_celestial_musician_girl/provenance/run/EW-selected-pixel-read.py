from pathlib import Path
from PIL import Image
import json
r=Path(__file__).resolve().parents[2]
rows=json.loads((r/'provenance/run/selection-EW.json').read_text(encoding='utf-8-sig'))
for x in rows:
 p=(r/x['file']).resolve()
 with Image.open(p) as im:
  a=im.getchannel('A');bb=a.point(lambda z:255 if z>128 else 0).getbbox()
  print(x['direction']+str(x['frame']).zfill(2),im.size,bb)


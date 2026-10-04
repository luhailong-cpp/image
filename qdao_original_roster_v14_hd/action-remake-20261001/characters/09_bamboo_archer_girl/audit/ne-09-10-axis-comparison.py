from PIL import Image,ImageDraw
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
d=json.loads((r/'audit/run-NE-09-10-axis-finish-review.json').read_text(encoding='utf-8'))
out=Image.new('RGBA',(1240,420),(232,237,229,255));draw=ImageDraw.Draw(out)
for j,f in enumerate(d['frames']):
 for k,key in enumerate(['beforeNative','afterNative']):
  im=Image.open(f[key]).resize((1024,1024));x=(j*2+k)*310
  out.alpha_composite(im.crop((550,760,860,1024)),(x,80))
  draw.text((x+12,25),f"NE{f['frame']:02d} "+('Before' if k==0 else 'After'),fill=(0,0,0))
out.save(r/'audit/NE-09-10-axis-comparison.png')
print('Incremental boot-axis comparison saved.')


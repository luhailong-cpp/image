from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
R=B.parents[1]
O=R/'10-delivery-preview/current'
Q=B/'qa-current'
M=json.loads((O/'manifest.json').read_text(encoding='utf-8'))
for d,ids,name in [('E',[3,4,5,6],'pass'),('SW',[5,6,13,14],'pass'),('E',[15,16,1,2],'seam'),('SW',[15,16,1,2],'seam')]:
 for bg,c in [('light','#f6f1e7'),('dark','#242a31')]:
  for part,box in [('feet',(290,740,730,980)),('head',(260,160,720,530))]:
   w,h=box[2]-box[0],box[3]-box[1]
   im=Image.new('RGB',(w*4,h+25),c);draw=ImageDraw.Draw(im)
   for j,n in enumerate(ids):
    key=d+f'{n:02}';row=M['frames'][key];p=O/row['file']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    f=Image.open(p).convert('RGBA');assert f.size==(1024,1024)
    crop=f.crop(box);im.paste(crop,(j*w,0),crop);draw.text((j*w+8,h+5),key,fill='white' if bg=='dark' else 'black')
   im.save(Q/f'final-{d}-{name}-{part}-{bg}.png')
print(M['createdAt'])

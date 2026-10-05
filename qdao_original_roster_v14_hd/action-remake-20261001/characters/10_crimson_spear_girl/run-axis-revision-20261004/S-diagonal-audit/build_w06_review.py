from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
w=Path(__file__).parent;root=w.parents[1]
files=[root/'runtime/run/W/05.png',root/'run-axis-revision-20261004/W/06-v2/native.png',root/'runtime/run/W/07.png']
out=Image.new('RGB',(1500,880),(231,231,223));d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
rows=[]
for i,p in enumerate(files):
 im=Image.open(p).convert('RGBA');n=im.resize((1024,1024),Image.Resampling.LANCZOS)
 thumb=n.resize((500,500),Image.Resampling.LANCZOS);out.paste(thumb,(i*500,30),thumb)
 feet=n.crop((290,680,750,990));out.paste(feet,(i*500+20,560),feet)
 d.text((i*500+12,3),['W05','W06-v2 (full canvas to1024)','W07'][i],font=font,fill=(20,20,20))
 d.line((i*500,0,i*500,880),fill=(160,160,150))
 rows.append({'file':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':list(im.size)})
out.save(w/'W06-independent-contact.jpg',quality=95)
(w/'W06-independent-source.json').write_text(json.dumps({'operation':'Inspection montage only; normalize whole native canvas to1024; fixed crop [290,680,750,990]; all source files read only','sources':rows},indent=2),encoding='utf-8')
print(json.dumps(rows))


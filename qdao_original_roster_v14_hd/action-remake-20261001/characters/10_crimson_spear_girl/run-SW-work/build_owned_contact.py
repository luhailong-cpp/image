from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parent
s=json.loads((root/'selection.json').read_text(encoding='utf8'))
im=Image.new('RGB',(1440,780),(232,235,237));d=ImageDraw.Draw(im)
for i,e in enumerate(s['entries']):
 a=Image.open(root/e['path']).convert('RGBA');a.thumbnail((360,360));x=i%4*360;y=i//4*390;im.paste(a,(x,y),a);d.text((x+8,y+365),e['slot'],fill=(20,20,20))
im.save(root/'SW09-16-contact.jpg',quality=93)
print('owned8 contact saved')

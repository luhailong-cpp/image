from pathlib import Path
from PIL import Image,ImageDraw
import json
d=Path(__file__).parent
s=json.loads((d/'selection.json').read_text())
sheet=Image.new('RGB',(1440,1280),'#e9e8e1')
dr=ImageDraw.Draw(sheet)
for i,(slot,f) in enumerate(s['slots'].items()):
 im=Image.open(d.parent/f).convert('RGBA')
 crop=im.crop((120,730,1100,1245)).resize((360,189))
 x=i%4*360;y=i//4*320
 sheet.paste(crop,(x,y),crop)
 dr.text((x+10,y+255),slot+' '+Path(f).stem,fill='#222')
sheet.save(d/'feet-audit.jpg',quality=96)


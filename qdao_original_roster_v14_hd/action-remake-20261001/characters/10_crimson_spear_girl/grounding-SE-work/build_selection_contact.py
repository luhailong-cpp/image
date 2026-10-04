from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parent
r=json.loads((root/'selection.json').read_text(encoding='utf8'))
board=Image.new('RGB',(1440,1560),(232,235,237));d=ImageDraw.Draw(board)
edges=[]
for i,e in enumerate(r['entries']):
 im=Image.open((root/e['path']).resolve()).convert('RGBA');a=im.getchannel('A');w,h=im.size
 c=dict(slot=e['slot'],rightBorderAlphaPixels=sum(v>10 for v in a.crop((w-1,0,w,h)).getdata()),alphaBox=a.getbbox())
 edges.append(c)
 im.thumbnail((360,360));x=(i%4)*360;y=(i//4)*390
 board.paste(im,(x,y),im);d.text((x+8,y+363),e['slot']+' '+e['path'][:22],fill=(20,25,35))
board.save(root/'SE-selected-contact.jpg',quality=92)
(root/'selected-edge-audit.json').write_text(json.dumps(edges,indent=2),encoding='utf8')
print(json.dumps(edges))

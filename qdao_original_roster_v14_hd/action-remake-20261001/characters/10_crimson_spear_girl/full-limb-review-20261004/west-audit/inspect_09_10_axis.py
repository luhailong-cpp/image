from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
r=Path(__file__).resolve().parents[2]
out=r/'full-limb-review-20261004/west-audit'
files=[r/'full-limb-review-20261004/run-NW/09-v4/native.png',r/'full-limb-review-20261004/run-NW/10-v1/native.png']
board=Image.new('RGB',(1400,1000),(235,235,228));d=ImageDraw.Draw(board)
for col,p in enumerate(files):
    im=Image.open(p)
    for row,(box,size) in enumerate([((340,470,455,625),(460,620)),((610,920,870,1150),(520,460))]):
        tile=im.crop(box).resize(size,Image.Resampling.NEAREST)
        if row==0:
            x,y=col*700,30
        else:
            x,y=col*700+130,530
        board.paste(tile,(x,y),tile)
    d.text((col*700+8,8),p.parent.name+' top / bottom fixed crops',fill=(0,0,0))
p=out/'NW09-v4_NW10-v1-rod-crops.jpg';board.save(p,quality=98)
p.with_suffix('.jpg.generation.json').write_text(json.dumps({'kind':'diagnostic-crops','method':'Pillow fixed crops; nearest enlargement; no asset modification','inputs':[{'file':str(x),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in files]},indent=2),encoding='utf-8')

from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[2]
for direction in ['NE','SE','NW']:
    out=B/'grounding4'/direction;out.mkdir(parents=True,exist_ok=True)
    canvas=Image.new('RGB',(1440,960),(225,225,219));d=ImageDraw.Draw(canvas);sources=[]
    for n in range(1,17):
        p=B/'runtime/run'/direction/f'{n:02d}.png';im=Image.open(p).convert('RGBA')
        crop=im.crop((270,660,790,980));crop.thumbnail((350,215))
        x=((n-1)%4)*360;y=((n-1)//4)*240
        canvas.paste(crop,(x+(360-crop.width)//2,y+23),crop);d.text((x+8,y+5),f'{direction} {n:02d}',fill=(0,0,0))
        sources.append({'frame':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':im.size})
    canvas.save(out/'runtime-feet-audit.jpg',quality=95)
    (out/'runtime-inputs.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


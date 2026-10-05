from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
OUT.mkdir(parents=True,exist_ok=True)
rows=[]
for direction in ['N','NE','E','SE']:
    for start in [1,9]:
        for area,box in [('hands',(170,355,980,760)),('legs',(150,650,980,1000))]:
            canvas=Image.new('RGB',(1200,4*330),'#eee9db')
            draw=ImageDraw.Draw(canvas)
            for j,num in enumerate(range(start,start+8)):
                p=ROOT/'runtime'/'run'/direction/f'{num:02d}.png'
                im=Image.open(p).convert('RGBA').crop(box)
                im.thumbnail((600,300),Image.Resampling.LANCZOS)
                x=(j%2)*600;y=(j//2)*330
                canvas.paste(im,(x+(600-im.width)//2,y+25),im)
                draw.text((x+10,y+5),f'run/{direction}/{num:02d} {area}',fill='#223b34')
                if area=='hands': rows.append({'slot':f'run/{direction}/{num:02d}','runtime':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
            canvas.save(OUT/f'north-{direction}-{start:02d}-{start+7:02d}-{area}.jpg',quality=96)
(OUT/'north-input-inventory.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print({'frames':len(rows),'sheets':16})

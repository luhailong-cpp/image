from pathlib import Path
from PIL import Image, ImageDraw
import json
root=Path(__file__).resolve().parents[2]
selected=json.loads((root/'provenance/run/selection-EW.json').read_text(encoding='utf-8-sig'))
for d in ['E','W']:
    entries=[]
    for n in range(1,17):
        p=(root/next(x['file'] for x in selected if x['action']=='run' and x['direction']==d and x['frame']==n)).resolve()
        entries.append(p)
    sheet=Image.new('RGB',(1280,1400),'#bfc7d2')
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(entries):
        im=Image.open(p).convert('RGBA'); im.thumbnail((320,320))
        x=(i%4)*320;y=(i//4)*350
        sheet.paste(im,(x,y),im);draw.line((x,y+294,x+320,y+294),fill='#57626d')
        draw.text((x+7,y+327),f'{d}{i+1:02d} {p.name}',fill='black')
    sheet.save(root/f'provenance/run/{d}-review-contact-current.jpg',quality=95)


from pathlib import Path
import json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[1]
W=B/'09-delivery-preview/work'
Q=B/'09-delivery-preview/east-qa'
Q.mkdir(exist_ok=True)
for d in ('E','NE'):
    fs=list((W/d/f'runtime/walk/{d}').glob('*.png'))
    for label,color in [('light',(235,228,214)),('dark',(34,39,45))]:
        sheet=Image.new('RGB',(1280,1360),color)
        draw=ImageDraw.Draw(sheet)
        for f in fs:
            n=int(f.stem)-1;x=n%4*320;y=n//4*340
            im=Image.open(f).convert('RGBA'); im.thumbnail((320,320))
            sheet.paste(im,(x,y+20),im)
            draw.text((x+10,y+5),f'{d} {n+1:02}',fill=(245,210,80) if label=='dark' else (30,35,40))
        sheet.save(Q/f'{d}-{label}-contact.png')
        if len(fs)==16:
            frames=[]
            for f in sorted(fs):
                im=Image.open(f).convert('RGBA');canvas=Image.new('RGBA',im.size,color+(255,));canvas.alpha_composite(im)
                frames.append(canvas.convert('RGB'))
            frames[0].save(Q/f'{d}-{label}-30ms.gif',save_all=True,append_images=frames[1:],duration=30,loop=0,disposal=2)
    print(d,len(fs))

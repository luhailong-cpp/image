from pathlib import Path
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[1]
I=B.parents[1]
for d in ['E','NE']:
    fs=sorted((I/f'qdao_original_roster_v13/candidate/00_reference_topright_boy/walk/{d}').glob('*.png'))
    out=Image.new('RGB',(1280,340*((len(fs)+3)//4)),(235,228,214));draw=ImageDraw.Draw(out)
    for n,f in enumerate(fs):
        im=Image.open(f).convert('RGBA');im.thumbnail((320,320));x=n%4*320;y=n//4*340
        out.paste(im,(x,y+20),im);draw.text((x+5,y+5),f.name,fill=(20,20,20))
    out.save(B/f'09-delivery-preview/east-qa/{d}-pose-guide.png')

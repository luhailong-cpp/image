from pathlib import Path
from PIL import Image,ImageDraw
import argparse
p=argparse.ArgumentParser();p.add_argument('direction');a=p.parse_args()
base=Path(__file__).resolve().parents[1];dest=base/'14-delivery-preview/assets'
for color,name in [('#252630','dark'),('#eee9df','light')]:
    out=Image.new('RGB',(1600,1680),color);dr=ImageDraw.Draw(out)
    for i in range(16):
        path=dest/f'walk/{a.direction}/{i+1:02}.png'
        if not path.exists(): continue
        im=Image.open(path).convert('RGBA');im.thumbnail((400,400));x=i%4*400;y=i//4*420
        out.paste(im,(x,y+20),im);dr.text((x+12,y+4),f'{a.direction} {i+1:02}',fill='#92929b')
    out.save(base/f'14-work-W-NW/{a.direction}-selected-{name}.jpg',quality=94)
    strips=Image.new('RGB',(2000,600),color)
    for i,slot in enumerate([15,16,1,2]):
        path=dest/f'walk/{a.direction}/{slot:02}.png'
        if not path.exists():continue
        im=Image.open(path).convert('RGBA');im=im.resize((500,500));strips.paste(im,(i*500,60),im)
        ImageDraw.Draw(strips).text((i*500+20,20),f'{a.direction} {slot:02}',fill='#92929b')
    strips.save(base/f'14-work-W-NW/{a.direction}-seam-{name}.jpg',quality=94)

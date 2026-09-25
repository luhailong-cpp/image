from pathlib import Path
from PIL import Image,ImageDraw
import argparse
HERE=Path(__file__).resolve().parent
CHAR='17_ghost_script_calligrapher_boy'
p=argparse.ArgumentParser();p.add_argument('--direction',default='N');a=p.parse_args();d=a.direction
can=Image.new('RGB',(2048,4*550),(30,38,46));dr=ImageDraw.Draw(can)
for i in range(1,17):
 v=2 if d=='N' and i==14 else ({6:2,9:3,13:3}.get(i,1) if d=='NE' else 1)
 f=HERE/f'staging/walk-{d}-{i:02d}-v{v}/candidate/{CHAR}/walk/{d}/{i:02d}.png'
 if not f.exists():continue
 im=Image.open(f).convert('RGBA');im.thumbnail((512,512));x=(i-1)%4*512;y=(i-1)//4*550
 can.paste(im,(x,y+30),im);dr.text((x+12,y+10),f'{d} {i:02d} v{v}',fill='white')
out=HERE/f'{d}-contact-review.png';can.save(out);print(out)

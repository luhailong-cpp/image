from pathlib import Path
from PIL import Image, ImageDraw
import sys
root=Path(__file__).resolve().parents[3]
direction=sys.argv[1]
source=root/'qdao_original_roster_v13/candidate/00_reference_topright_boy/walk'/direction
out=Path(__file__).parent/'west-review'
out.mkdir(exist_ok=True)
sheet=Image.new('RGB',(1024,1160),(32,40,48))
draw=ImageDraw.Draw(sheet)
for n in range(1,17):
    im=Image.open(source/f'{n:02}.png').convert('RGBA'); im.thumbnail((256,256))
    x=(n-1)%4*256; y=(n-1)//4*290
    sheet.paste(im,(x,y+28),im)
    draw.text((x+10,y+8),f'{direction}{n:02}',fill='white')
sheet.save(out/f'pose-guide-{direction}.png')
print(out/f'pose-guide-{direction}.png')

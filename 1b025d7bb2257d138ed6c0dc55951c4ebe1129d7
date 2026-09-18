from pathlib import Path
from PIL import Image,ImageDraw
r=Path('E:/work/image/qdao_original_roster_v13'); im=Image.open(r/'generation/00_reference_topright_boy/walk-S-anchors-v2/raw.png').convert('RGB'); w,h=im.size; cells=[im.crop((round(c*w/2),round(y*h/2),round((c+1)*w/2),round((y+1)*h/2))) for y in range(2) for c in range(2)]
for i in range(4):
 board=Image.new('RGB',(800,425),(40,44,45));d=ImageDraw.Draw(board);d.text((10,5),'A: start',fill='white');d.text((410,5),'B: end',fill='white');board.paste(cells[i].resize((400,400)),(0,25));board.paste(cells[(i+1)%4].resize((400,400)),(400,25));board.save(r/f'review/00_reference_topright_boy/S-pair-{i+1}.jpg',quality=72,optimize=True)
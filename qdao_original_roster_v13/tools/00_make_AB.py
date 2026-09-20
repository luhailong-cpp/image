from pathlib import Path
from PIL import Image,ImageDraw
r=Path('E:/work/image/qdao_original_roster_v13'); im=Image.open(r/'generation/00_reference_topright_boy/walk-S-anchors-v2/raw.png').convert('RGB'); w,h=im.size;cells=[im.crop((round(c*w/2),round(y*h/2),round((c+1)*w/2),round((y+1)*h/2))) for y in range(2) for c in range(2)];board=Image.new('RGB',(1000,520),(40,44,45));d=ImageDraw.Draw(board);d.text((10,5),'A: start poses 1,5,9,13',fill='white');d.text((510,5),'B: target poses 5,9,13,1',fill='white')
for side,order in enumerate(([0,1,2,3],[1,2,3,0])):
 for slot,idx in enumerate(order):
  y,c=divmod(slot,2);board.paste(cells[idx].resize((250,250)),(side*500+c*250,20+y*250))
board.save(r/'review/00_reference_topright_boy/S-anchor-AB.jpg',quality=70,optimize=True)
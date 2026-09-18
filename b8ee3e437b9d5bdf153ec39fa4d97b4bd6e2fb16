from pathlib import Path
from PIL import Image
r=Path('E:/work/image/qdao_original_roster_v13');im=Image.open(r/'generation/00_reference_topright_boy/walk-S-anchors-v2/raw.png').convert('RGB');w,h=im.size;cells=[im.crop((round(c*w/2),round(y*h/2),round((c+1)*w/2),round((y+1)*h/2))) for y in range(2) for c in range(2)]
for label,order in [('A',[0,1,2,3]),('B',[1,2,3,0])]:
 board=Image.new('RGB',(900,900),(255,0,255))
 for slot,idx in enumerate(order):
  y,x=divmod(slot,2);board.paste(cells[idx].resize((450,450)),(x*450,y*450))
 board.save(r/f'review/00_reference_topright_boy/S-reference-{label}.jpg',quality=76,optimize=True)
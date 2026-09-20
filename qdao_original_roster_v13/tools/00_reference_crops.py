from PIL import Image
from pathlib import Path
r=Path('E:/work/image/qdao_original_roster_v13'); im=Image.open(r/'generation/00_reference_topright_boy/idle-eightdir-v1/raw.png').convert('RGBA'); w,h=im.size; out=r/'review/00_reference_topright_boy'
for d,i in [('E',6),('S',4)]:
 y,x=divmod(i,4); c=im.crop((round(x*w/4),round(y*h/2),round((x+1)*w/4),round((y+1)*h/2))); bg=Image.new('RGB',c.size,(50,56,60));bg.paste(c,(0,0),c);bg.save(out/f'idle-{d}-reference.jpg',quality=83)
print(im.size)
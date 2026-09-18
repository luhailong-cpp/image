from PIL import Image
from pathlib import Path
r=Path(r'E:\work\image\qdao_original_roster_v13')
p=r/'generation/00_reference_topright_boy/SE-final-repair'
for f in p.glob('*-source-cell.png'):Image.open(f).convert('RGB').save(f.with_name(f.name.replace('-source-cell.png','-reference.jpg')),quality=88)
for d in ['N','W','SW','NW']:
 im=Image.open(r/f'candidate/00_reference_topright_boy/review/{d}-contact.png');im.resize((1100,round(im.height*1100/im.width))).save(r/f'review/00_reference_topright_boy/{d}-full-contact.jpg',quality=84)

from PIL import Image
from pathlib import Path
r=Path(r'E:\work\image\qdao_original_roster_v13')
for d in ['N','NE','E','SE','S','SW','W','NW']:
 im=Image.open(r/f'candidate/00_reference_topright_boy/review/{d}-contact.png');im.resize((1100,round(im.height*1100/im.width))).save(r/f'review/00_reference_topright_boy/{d}-full-contact.jpg',quality=84)
for f in [12,13,14]:
 im=Image.open(r/f'candidate/00_reference_topright_boy/walk/SE/{f:02d}.png').convert('RGBA');a=im.getchannel('A');b=a.point(lambda v:255 if v>32 else 0).getbbox();band=a.crop((0,b[1],512,b[1]+round((b[3]-b[1])*.35))).point(lambda v:255 if v>32 else 0).getbbox();print(f,b,'height',b[3]-b[1],'headband_width',band[2]-band[0])

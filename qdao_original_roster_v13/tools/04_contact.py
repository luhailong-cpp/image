from pathlib import Path
from PIL import Image,ImageDraw
root=Path(r'E:/work/image/qdao_original_roster_v13'); ch='04_mountain_guardian_boy';out=root/'candidate'/ch/'review'
for p in (root/'generation'/ch/'E-anchors').glob('*.png'):Image.open(p).convert('RGB').save(p.with_suffix('.jpg'),quality=92)
b=Image.new('RGB',(1024,1120),(235,235,226));d=ImageDraw.Draw(b)
for f in range(1,17):
 im=Image.open(root/'candidate'/ch/'walk/S'/f'{f:02}.png').convert('RGBA');im=im.resize((256,256));x=((f-1)%4)*256;y=((f-1)//4)*280;b.paste(im,(x,y+20),im);d.text((x+10,y+4),f'S {f:02}',fill=(20,20,20))
b.save(out/'S-full-contact.jpg',quality=92)

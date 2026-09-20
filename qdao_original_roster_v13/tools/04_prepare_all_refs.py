from pathlib import Path
from PIL import Image,ImageDraw
import subprocess,sys
root=Path(r'E:/work/image/qdao_original_roster_v13');ch='04_mountain_guardian_boy'
for direction in ['W','N','SW','SE','NE']:
 subprocess.run([sys.executable,'-B',str(root/'tools/prepare_references.py'),'--character',ch,'--direction',direction,'--frames','1,5,9,13','--name','anchors'],check=True)
 for p in (root/'generation'/ch/(direction+'-anchors')).glob('*.png'):Image.open(p).convert('RGB').save(p.with_suffix('.jpg'),quality=92)
for direction in ['S','E']:
 b=Image.new('RGB',(1024,1120),(235,235,226));d=ImageDraw.Draw(b)
 for f in range(1,17):
  im=Image.open(root/'candidate'/ch/'walk'/direction/f'{f:02}.png').convert('RGBA').resize((256,256));x=((f-1)%4)*256;y=((f-1)//4)*280;b.paste(im,(x,y+20),im);d.text((x+10,y+4),f'{direction} {f:02}',fill=(20,20,20))
 b.save(root/'candidate'/ch/'review'/(direction+'-full-contact.jpg'),quality=92)

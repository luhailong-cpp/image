from pathlib import Path
import subprocess
from PIL import Image
root=Path(r'E:\work\image\qdao_original_roster_v13')
py=r'C:\Users\luyua\AppData\Local\Programs\Python\Python312\python.exe'
requests=[('N','10,12','repair11'),('NW','1,9,11,13,15','repair12-14'),('W','11,13','repair12'),('SW','2,4,14,16','repair3-15'),('E','5,6,7,11,12,13','repairarms')]
for d,fs,n in requests:
 subprocess.run([py,str(root/'tools/prepare_references.py'),'--character','00_reference_topright_boy','--direction',d,'--frames',fs,'--name',n],check=True)
 p=root/'generation/00_reference_topright_boy'/f'{d}-{n}'
 for f in p.glob('*-source-cell.png'):Image.open(f).convert('RGB').save(f.with_name(f.name.replace('-source-cell.png','-reference.jpg')),quality=88)
c=root/'candidate/00_reference_topright_boy'
im=Image.open(c/'review/NE-contact.png');im.resize((1100,round(im.height*1100/im.width))).save(root/'review/00_reference_topright_boy/NE-full-contact.jpg',quality=84)
for f in [9,10,11,12,13]:
 im=Image.open(c/f'walk/NE/{f:02d}.png').convert('RGBA');a=im.getchannel('A');b=a.point(lambda v:255 if v>32 else 0).getbbox()
 band=a.crop((0,b[1],512,b[1]+round((b[3]-b[1])*.35))).point(lambda v:255 if v>32 else 0).getbbox()
 print(f,b,'height',b[3]-b[1],'upper35width',band[2]-band[0])

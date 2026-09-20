from pathlib import Path
from PIL import Image
r=Path('E:/work/image/qdao_original_roster_v13/generation/00_reference_topright_boy')
b=Image.new('RGB',(1024,1024),(255,0,255))
for i,f in enumerate([9,13,9,13]):
 im=Image.open(r/f'NE-corrected-endpoints/{f:02d}-source-cell.png').convert('RGB');y,x=divmod(i,2);b.paste(im,(512*x,512*y))
b.resize((900,900)).save(r/'NE-corrected-endpoints/size-reference-board.jpg',quality=83)
im=Image.open(r/'walk-NE-10-11-12-size-v4/raw.png').convert('RGBA');b=Image.new('RGB',im.size,(255,0,255));b.paste(im,(0,0),im);b.resize((900,900)).save(r/'walk-NE-10-11-12-size-v4/reference.jpg',quality=83)
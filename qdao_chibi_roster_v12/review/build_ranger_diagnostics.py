from pathlib import Path
from PIL import Image,ImageDraw
c=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\27_ink_kite_ranger');out=c/'review';out.mkdir(exist_ok=True)
for d in ['N','NE','E','SE','S','SW','W','NW']:
 p=c/'processing/alignment-v3'/d
 board=Image.new('RGBA',(768,840),'#e8e3d9');draw=ImageDraw.Draw(board)
 for i,f in enumerate(['idle.png']+[f'{j:02d}.png' for j in range(1,9)]):
  im=Image.open(p/f).convert('RGBA');board.alpha_composite(im.resize((256,256)),(i%3*256,i//3*280+24));draw.text((i%3*256+8,i//3*280+6),d+' '+f,fill='#243d35')
 board.convert('RGB').save(out/f'{d}-idle-walk.jpg',quality=91)
print('27 diagnostic contact boards generated from processing output only; no failed QC bypass')


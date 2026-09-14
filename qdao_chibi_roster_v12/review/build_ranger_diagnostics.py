from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
c=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\27_ink_kite_ranger');out=c/'review';out.mkdir(exist_ok=True)
transforms=json.loads((c/'processing/frame-transforms.json').read_text())
for d in ['N','NE','E','SE','S','SW','W','NW']:
 p=c/'processing/alignment-v3'/d
 board=Image.new('RGBA',(768,840),'#e8e3d9');draw=ImageDraw.Draw(board)
 for i,f in enumerate(['idle.png']+[f'{j:02d}.png' for j in range(1,9)]):
  im=Image.open(p/f).convert('RGBA');tr=transforms['idle'][d] if i==0 else transforms['walk'][d][i-1];assert list(im.size)==tr['resized_crop_size'];canvas=Image.new('RGBA',(512,512));canvas.paste(im,tuple(tr['translation_px']));assert hashlib.sha256(canvas.tobytes()).hexdigest()==tr['rgba_sha256'];board.alpha_composite(canvas.resize((256,256)),(i%3*256,i//3*280+24));draw.text((i%3*256+8,i//3*280+6),d+' '+f,fill='#243d35')
 board.convert('RGB').save(out/f'{d}-idle-walk.jpg',quality=91)
print('27 diagnostic contact boards generated from processing output only; no failed QC bypass')


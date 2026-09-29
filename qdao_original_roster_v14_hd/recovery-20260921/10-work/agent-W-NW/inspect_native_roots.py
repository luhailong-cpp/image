from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
H=Path(__file__).resolve().parent
R=H.parents[1]
S=json.loads((H/'selection-NW-review.json').read_text())
rows=[]
for start in [1,5,9,13]:
 sh=Image.new('RGB',(4*500,500),'#f0ede5');d=ImageDraw.Draw(sh)
 for j in range(4):
  n=start+j;k=f'NW{n:02}';a=S[k]['archive'];im=Image.open(R/'10-generation'/a/'raw.png').convert('RGBA')
  ar=np.asarray(im)[:,:,3]; y,x=np.where(ar>8)
  crop=im.crop((300,800,1000,1254));crop=crop.resize((500,324))
  sh.paste(crop,(j*500,60),crop)
  d.text((j*500+10,15),f'{k} {a} maxY={int(y.max())}',fill='black')
  for yy in range(850,1251,50):
   line=60+round((yy-800)*500/700);d.line((j*500,line,(j+1)*500,line),fill='#99aa99');d.text((j*500+3,line),str(yy),fill='black')
  for xx in range(400,1001,100):
   line=j*500+round((xx-300)*500/700);d.line((line,60,line,384),fill='#99aa99');d.text((line,390),str(xx),fill='black')
  rows.append({'slot':k,'attempt':a,'nativeMaxAlphaY':int(y.max())})
 sh.save(H/'wnw-qa-20260928'/f'NW-native-feet-grid-{start:02}.jpg',quality=96)
(H/'wnw-qa-20260928'/'native-maxima.json').write_text(json.dumps(rows,indent=2))

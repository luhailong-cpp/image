from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent.parent
im=Image.open(R/'tiles/r10_c12-candidate.png').convert('RGB')
for y in [2048,3072]:
 out=Image.new('RGB',(1024,1120),(235,235,235));d=ImageDraw.Draw(out)
 for c in range(4):
  d.text((4,c*280),f'y={y},x={c*1024}..{(c+1)*1024}',fill='black');out.paste(im.crop((c*1024,y-128,(c+1)*1024,y+128)),(0,c*280+24))
 out.save(R/'evidence'/f'independent-y{y}-native.png')
out=Image.new('RGB',(768,1048),(235,235,235));d=ImageDraw.Draw(out)
for c,x in enumerate([1024,2048,3072]):
 d.text((c*256+4,0),f'x={x},y=3072..4096',fill='black');out.paste(im.crop((x-128,3072,x+128,4096)),(c*256,24))
out.save(R/'evidence/independent-bottom-vertical-native.png')

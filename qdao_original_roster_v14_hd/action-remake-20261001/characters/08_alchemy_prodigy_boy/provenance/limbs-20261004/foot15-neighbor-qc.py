from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
canvas=Image.new('RGB',(1200,730),'#eee9db');draw=ImageDraw.Draw(canvas)
for k,n in enumerate([14,15,16]):
 p=ROOT/'generation/limbs-20261004/foot-ne15/NE15-v2.png' if n==15 else ROOT/'generation/limbs-20261004/foot-ne14/14-v4.png' if n==14 else ROOT/'runtime/run/NE'/f'{n:02d}.png'
 im=Image.open(p).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
 tile=im.resize((400,400),Image.Resampling.LANCZOS);canvas.paste(tile,(k*400,25),tile)
 crop=im.crop((250,640,850,990));crop.thumbnail((400,300),Image.Resampling.LANCZOS);canvas.paste(crop,(k*400,445),crop)
 draw.text((k*400+10,5),f'NE/{n:02d} '+('candidate v2' if n==15 else 'candidate v4' if n==14 else 'current'),fill='#203b32')
canvas.save(OUT/'foot15-neighbor-contact.jpg',quality=96)

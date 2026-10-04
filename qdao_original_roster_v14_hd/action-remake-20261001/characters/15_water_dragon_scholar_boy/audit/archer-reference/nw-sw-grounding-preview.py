from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
B=Path(__file__).resolve().parents[2]
q=json.loads((B/'audit/archer-reference/nw-sw-grounding-selection.json').read_text(encoding='utf-8-sig'))
rows=q['rows'];font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
frames={}
for r in rows:
 im=Image.open(r['file']).convert('RGBA')
 if im.size==(1254,1254):
  dst=Image.new('RGBA',(1024,1024));dst.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));im=dst
 frames[r['slot']]=im.resize((320,320),Image.Resampling.LANCZOS)
anim=[]
for t in range(32):
 out=Image.new('RGB',(640,720),(225,230,227));d=ImageDraw.Draw(out)
 for y,di in enumerate(['NW','SW']):
  for x in range(2):
   n=t%16+1 if x==0 else t//2+1
   r=next(r for r in rows if r['slot']==f'run/{di}/{n:02}')
   im=frames[r['slot']];out.paste(im,(320*x,360*y+28),im)
   label=f"{di} {'1x / 75ms' if x==0 else '0.5x / 150ms'} 帧{n:02}"
   d.text((320*x+8,360*y+4),label,font=font,fill=(20,35,35))
   d.text((320*x+8,360*y+338),r['grounding']['spatialStage'],font=font,fill=(20,35,35))
 anim.append(out)
path=B/'audit/archer-reference/nw-sw-grounding-preview.png'
anim[0].save(path,save_all=True,append_images=anim[1:],duration=75,loop=0,disposal=0)
print(path)


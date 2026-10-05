from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
B=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
groups=[('E02-05','E',[2,3,4,5]),('W02-05','W',[2,3,4,5]),('E10-12','E',[10,11,12]),('W10-12','W',[10,11,12])]
sheet=Image.new('RGB',(1000,4*270),(47,52,57));draw=ImageDraw.Draw(sheet);data=[]
for row,(label,d,frames) in enumerate(groups):
 for i,f in enumerate(frames):
  p=B/'runtime/run'/d/f'{f:02}.png'; im=Image.open(p).convert('RGBA')
  q=im.resize((240,240),Image.Resampling.LANCZOS); sheet.paste(q,(i*250,row*270+24),q);draw.text((i*250+8,row*270+5),f'{d}{f:02}',fill='white')
  data.append({'direction':d,'frame':f,'file':str(p.relative_to(B)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
sheet.save(O/'handoff-trajectories-240.jpg',quality=95)
(O/'handoff-trajectories-inputs.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(O/'handoff-trajectories-240.jpg')


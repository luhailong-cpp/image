from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib
ROOT=Path(__file__).resolve().parents[2]
for action,direction in [('cast','E'),('cast','W'),('run','SE')]:
 paths=sorted((ROOT/'frames'/action/direction).glob('frame_*.png'))
 im=Image.new('RGB',(1280,1400),'#f3eee2')
 draw=ImageDraw.Draw(im)
 font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
 for i,p in enumerate(paths):
  x=i%4*320;y=i//4*350
  src=Image.open(p).convert('RGBA').resize((320,320),Image.Resampling.LANCZOS)
  im.paste(src,(x,y+28),src)
  draw.text((x+8,y+3),f'{action} {direction} {i+1:02}',fill='#20372b',font=font)
 out=ROOT/'provenance'/action/f'{direction}_current_contact.png'
 im.save(out)
 meta={'file':str(out.relative_to(ROOT)).replace('\\\\','/'),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'modelGenerated':False,'operation':{'type':'deterministic_contact_sheet','sourceWholeCanvas':True,'poseEditing':False},'derivedFrom':[{'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':p.with_suffix('.generation.json').relative_to(ROOT).as_posix()} for p in paths]}
 out.with_name(out.name+'.generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(str(out))

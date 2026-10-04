from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[2]
action=sys.argv[1]; direction=sys.argv[2]; count=16
dest=root/'provenance'/action
sheet=Image.new('RGB',(1120,1240),'#eee7d5')
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
sources=[]
for i in range(1,count+1):
 p=root/'frames'/action/direction/f'frame_{i:02}.png'
 x=((i-1)%4)*280;y=((i-1)//4)*310
 draw.text((x+8,y+7),f'{action} {direction} {i:02}',font=font,fill='#253525')
 if p.exists():
  im=Image.open(p).convert('RGBA').resize((280,280),Image.Resampling.LANCZOS)
  sheet.paste(im,(x,y+30),im)
  sources.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out=dest/f'{direction}_contact_current.png'
sheet.save(out)
(out.with_suffix('.png.generation.json')).write_text(json.dumps({'file':str(out),'operation':'deterministic_review_contact','modelGenerated':False,'derivedFrom':sources},ensure_ascii=False,indent=2),encoding='utf8')
print(out)


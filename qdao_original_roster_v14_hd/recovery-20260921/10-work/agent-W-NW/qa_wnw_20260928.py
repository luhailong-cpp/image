from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
HERE=Path(__file__).resolve().parent
base=HERE.parents[1]/'10-delivery-preview/current'
out=HERE/'wnw-qa-20260928'
out.mkdir(exist_ok=True)
bindings=[]
for direction in ['W','NW']:
 for name in ['idle']+[f'{i:02}' for i in range(1,17)]:
  p=base/'idle'/f'{direction}.png' if name=='idle' else base/'walk'/direction/f'{name}.png'
  bindings.append({'direction':direction,'slot':name,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for theme,color in [('dark','#18212c'),('light','#f0ede5')]:
  for group in [range(1,9),range(9,17),[15,16,1,2]]:
   size=384 if len(group)==8 else 512
   sheet=Image.new('RGB',(size*4,(size+30)*(2 if len(group)==8 else 1)),color)
   draw=ImageDraw.Draw(sheet)
   for k,i in enumerate(group):
    im=Image.open(base/'walk'/direction/f'{i:02}.png').convert('RGBA');im.thumbnail((size,size))
    x=(k%4)*size;y=(k//4)*(size+30)
    sheet.paste(im,(x,y),im);draw.text((x+10,y+size+4),f'{direction}{i:02}',fill='white' if theme=='dark' else 'black')
   sheet.save(out/f'{direction}-{theme}-{list(group)[0]:02}-{list(group)[-1]:02}.jpg',quality=95)
  for group in [range(1,9),range(9,17)]:
   sheet=Image.new('RGB',(4*512,2*344),color);draw=ImageDraw.Draw(sheet)
   for k,i in enumerate(group):
    im=Image.open(base/'walk'/direction/f'{i:02}.png').convert('RGBA').crop((250,650,762,964))
    x=(k%4)*512;y=(k//4)*344
    sheet.paste(im,(x,y),im);draw.text((x+10,y+317),f'{direction}{i:02}',fill='white' if theme=='dark' else 'black')
   sheet.save(out/f'{direction}-{theme}-feet-{list(group)[0]:02}.jpg',quality=95)
  im=Image.open(base/'idle'/f'{direction}.png').convert('RGBA');im.thumbnail((768,768))
  idle=Image.new('RGB',(768,768),color);idle.paste(im,(0,0),im);idle.save(out/f'{direction}-{theme}-idle.jpg',quality=95)
(out/'sha-bindings.json').write_text(json.dumps({'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':bindings},indent=2)+'\n')
print(out)

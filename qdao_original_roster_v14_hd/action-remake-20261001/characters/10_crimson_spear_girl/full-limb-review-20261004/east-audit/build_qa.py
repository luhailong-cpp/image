from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
w=Path(__file__).parent;root=w.parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
rows=[]
regions={'upper':(280,400,820,810),'lower':(230,600,820,990)}
for dr in ['E','NE','SE']:
 full=Image.new('RGB',(1280,1400),(234,234,225));fd=ImageDraw.Draw(full)
 for n in range(1,17):
  p=root/f'runtime/run/{dr}/{n:02d}.png';im=Image.open(p).convert('RGBA')
  assert im.size==(1024,1024)
  thumb=im.resize((320,320),Image.Resampling.LANCZOS)
  x=((n-1)%4)*320;y=((n-1)//4)*350
  full.paste(thumb,(x,y+28),thumb);fd.text((x+8,y+3),f'{dr} {n:02d}',font=font,fill='black')
  rows.append({'slot':f'run/{dr}/{n:02d}','file':p.relative_to(root).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':[1024,1024],'reviewStatus':'unreviewed'})
 full.save(w/f'{dr}-full.jpg',quality=94)
 for start in [1,9]:
  for region,box in regions.items():
   tw,th=box[2]-box[0],box[3]-box[1]
   sheet=Image.new('RGB',(tw*4,(th+30)*2),(234,234,225));d=ImageDraw.Draw(sheet)
   for i,n in enumerate(range(start,start+8)):
    p=root/f'runtime/run/{dr}/{n:02d}.png';im=Image.open(p).convert('RGBA').crop(box)
    x=(i%4)*tw;y=(i//4)*(th+30)
    sheet.paste(im,(x,y+30),im);d.text((x+8,y+3),f'{dr} {n:02d} | {region}',font=font,fill='black')
    d.line((x,y,x,y+th+30),fill=(160,160,150))
   sheet.save(w/f'{dr}-{start:02d}-{start+7:02d}-{region}.jpg',quality=95)
(w/'frames.json').write_text(json.dumps({'status':'in-progress','sourceRoot':str(root),'scope':['run/E','run/NE','run/SE'],'sourceReadAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewPolicy':'Every frame visual inspection of full fixed canvas and fixed upper/lower crops; source SHA is identity evidence only','cropBoxes':regions,'frameMs':75,'contactRule':'Each successive contact position has two distinct poses; no central four-frame hold or frame duplication','frames':rows},indent=2),encoding='utf-8')
print('48 current runtime SHA captured; fixed QA sheets created; all statuses still unreviewed.')


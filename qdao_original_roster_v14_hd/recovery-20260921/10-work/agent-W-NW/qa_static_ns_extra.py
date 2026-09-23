import pathlib,json,hashlib
from PIL import Image,ImageDraw
folder=pathlib.Path(__file__).resolve().parent
base=folder.parents[1]/'10-delivery-preview/current'
out=folder/'ns-static-review'
for theme,color in [('dark','#18212c'),('light','#f0ede5')]:
 for direction in ['N','S']:
  sheet=Image.new('RGB',(2000,940),color);draw=ImageDraw.Draw(sheet)
  for k,i in enumerate([2,4,6,8,10,12,14,16]):
   im=Image.open(base/'walk'/direction/f'{i:02}.png').convert('RGBA').crop((270,680,770,1120))
   x=(k%4)*500;y=(k//4)*470;sheet.paste(im,(x,y),im)
   draw.text((x+10,y+443),f'{direction}{i:02}',fill='white' if theme=='dark' else 'black')
  sheet.save(out/f'{direction}-{theme}-legs-even.jpg',quality=95)
 sheet=Image.new('RGB',(1536,768),color);draw=ImageDraw.Draw(sheet)
 for k,direction in enumerate(['N','S']):
  im=Image.open(base/'idle'/f'{direction}.png').convert('RGBA').resize((768,768),Image.Resampling.LANCZOS)
  sheet.paste(im,(k*768,0),im);draw.text((k*768+20,740),f'{direction} idle',fill='white' if theme=='dark' else 'black')
 sheet.save(out/f'idle-{theme}.jpg',quality=95)
bindings=json.loads((out/'sha-bindings.json').read_text())
changed=[x['path'] for x in bindings['files'] if hashlib.sha256(pathlib.Path(x['path']).read_bytes()).hexdigest()!=x['sha256']]
print('Changed since review snapshot:',changed)

import pathlib,json,hashlib,datetime
from PIL import Image,ImageDraw
folder=pathlib.Path(__file__).resolve().parent
base=folder.parents[1]/'10-delivery-preview/current'
sel=folder/'selection-W-review.json'
d=json.loads(sel.read_text())
if d['W07']['archive']=='W07-v1':
 d['W07'],d['W08']=d['W08'],d['W07']
 for slot in ['W07','W08']:
  d[slot]['review']+='; reordered 2026-09-23 after direct comparison: actual forward boot clearance decreases W06-v2 > W08-v1 > W07-v1 > W09-v8; distinct AI originals, no pixels synthesized'
 sel.write_text(json.dumps(d,indent=2)+'\n')
out=folder/'ns-static-review'
out.mkdir(exist_ok=True)
bindings=[]
for direction in ['N','S']:
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
  leg=Image.new('RGB',(4*500,2*470),color);draw=ImageDraw.Draw(leg)
  for k,i in enumerate([1,3,5,7,9,11,13,15]):
   im=Image.open(base/'walk'/direction/f'{i:02}.png').convert('RGBA').crop((270,680,770,1120))
   x=(k%4)*500;y=(k//4)*470
   leg.paste(im,(x,y),im);draw.text((x+10,y+443),f'{direction}{i:02}',fill='white' if theme=='dark' else 'black')
  leg.save(out/f'{direction}-{theme}-legs.jpg',quality=95)
(out/'sha-bindings.json').write_text(json.dumps({'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':bindings},indent=2)+'\n')
print(out)

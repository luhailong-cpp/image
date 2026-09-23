from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1]
out=R/'14-work-NE';out.mkdir(exist_ok=True)
assets=R/'14-delivery-preview/assets/walk/NE'
for label,bg in [('light',(244,239,226,255)),('dark',(29,39,50,255))]:
 sheet=Image.new('RGBA',(1024,1120),bg);d=ImageDraw.Draw(sheet)
 for i in range(1,17):
  p=assets/f'{i:02d}.png'
  if not p.exists():continue
  im=Image.open(p).convert('RGBA');im.thumbnail((256,256));x=((i-1)%4)*256;y=((i-1)//4)*280
  sheet.alpha_composite(im,(x,y));d.text((x+8,y+257),f'NE {i:02d}',fill=(130,100,100,255))
 sheet.convert('RGB').save(out/f'NE-selected-{label}.jpg',quality=94)
files=[]
for i in [1,2,14,16]:
 p=assets/f'{i:02d}.png';m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
 files.append({'frame':i,'file':str(p),'sourceArchive':m['sourceArchive'],'finalSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSHA256':m['derivedFrom']['sha256'],'nativeSize':m['nativeSize'],'alphaMode':m['nativeMode'],'actualModel':m['actualModel'],'actualQuality':m['actualQuality']})
(out/'selected-finalize-ne.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

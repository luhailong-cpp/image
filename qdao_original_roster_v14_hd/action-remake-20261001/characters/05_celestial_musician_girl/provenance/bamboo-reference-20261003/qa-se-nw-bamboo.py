from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
r=Path(__file__).resolve().parents[2]
b=r.parent/'09_bamboo_archer_girl'
out=Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((b/'manifest.json').read_text(encoding='utf-8-sig'))
snapshot={'bambooManifestPath':str(b/'manifest.json'),'bambooManifestSha256':sha(b/'manifest.json'),'rows':[]}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for direction in ['SE','NW']:
 sequence=next(s for s in m['sequences'] if s['action']=='run' and s['direction']==direction)
 for who in ['bamboo','musician']:
  canvas=Image.new('RGB',(1280,1408),(220,224,227));draw=ImageDraw.Draw(canvas)
  for idx,f in enumerate(sequence['frames']):
   num=f['frame'];p=b/f['file'] if who=='bamboo' else r/f'final/run/{direction}/{num:02d}.png'
   h=sha(p); im=Image.open(p).convert('RGBA')
   if who=='bamboo': assert h==f['sha256']
   snapshot['rows'].append({'character':who,'direction':direction,'frame':num,'path':str(p),'sha256':h,'size':list(im.size)})
   im=im.resize((320,320),Image.Resampling.LANCZOS)
   x=(idx%4)*320;y=(idx//4)*352
   canvas.paste(im,(x,y),im);draw.text((x+8,y+323),f'{who} {direction} {num:02d}',font=font,fill=(0,0,0))
  canvas.save(out/f'run-{direction}-{who}.jpg',quality=95)
(out/'SE-NW-source-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifestSHA':snapshot['bambooManifestSha256'],'rows':len(snapshot['rows'])}))


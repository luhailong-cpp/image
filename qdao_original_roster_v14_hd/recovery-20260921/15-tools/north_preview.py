from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'15-review/north-previews';O.mkdir(exist_ok=True)
manifest=[]
for d in ['N','NE']:
 rows=[R/'15-delivery-preview/runtime/walk'/d/f'{i:02}.png' for i in range(1,17)]
 for bg,name in [((240,234,220),'light'),((24,34,44),'dark')]:
  seq=[]
  for p in rows:
   im=Image.open(p).convert('RGBA');b=Image.new('RGB',(1024,1024),bg);b.paste(im,(0,0),im);seq.append(b.resize((512,512),Image.Resampling.LANCZOS))
  gif=O/f'{d}-{name}-30ms.gif';seq[0].save(gif,save_all=True,append_images=seq[1:],duration=30,loop=0,disposal=2)
  check=Image.open(gif);dur=[]
  for n in range(check.n_frames):check.seek(n);dur.append(check.info['duration'])
  assert dur==[30]*16
  manifest.append({'direction':d,'file':str(gif),'sha256':hashlib.sha256(gif.read_bytes()).hexdigest(),'frameDurationsMs':dur,'cycleMs':sum(dur),'sourceSha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in rows],'observation':'encoded timing decoded; motion perception not verified by this script'})
  for start in range(1,17,4):
   # All four 1:1 edge crops, head+fan/sleeve separated from shoe review.
   sheet=Image.new('RGB',(1400,1600),bg);draw=ImageDraw.Draw(sheet)
   for k,p in enumerate(rows[start-1:start+3]):
    im=Image.open(p).convert('RGBA').crop((175,100,875,900));x=(k%2)*700;y=(k//2)*800;sheet.paste(im,(x,y),im);draw.text((x+8,y+5),f'{d}{start+k:02} 1:1 pixels',fill=(80,160,180))
   sheet.save(O/f'{d}-{start:02}-{start+3:02}-{name}-large.png')
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

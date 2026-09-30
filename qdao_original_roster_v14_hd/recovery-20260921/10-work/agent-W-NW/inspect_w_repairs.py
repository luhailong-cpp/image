from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[1];O=H/'static-review-final-20260928'
rows=[]
for a in ['W06-v7','W14-v5']:
 im=Image.open(R/'10-generation'/a/'raw.png').convert('RGBA');fac=1024/im.width*.84;n=im.resize((860,860),Image.Resampling.LANCZOS);f=Image.new('RGBA',(1024,1024));f.paste(n,(round(512-500*860/1254),round(942-1195*860/1254)))
 for t,col in [('light','#f0ede5'),('dark','#18212c')]:
  comp=Image.new('RGBA',f.size,col);comp.alpha_composite(f);comp.convert('RGB').save(O/f'{a}-{t}-normal.jpg',quality=98)
  sh=Image.new('RGB',(1536,768),col)
  for j,box in enumerate([(270,570,654,954),(290,190,674,574),(615,190,999,574)]):
   cr=comp.crop(box).resize((768,768));sh.paste(cr,(j%2*768,j//2*0))
   cr.convert('RGB').save(O/f'{a}-{t}-zoom-{j}.jpg',quality=98)
 rows.append({'attempt':a,'native':im.size,'rgba':im.mode,'alphaRange':im.getchannel('A').getextrema(),'sha256':hashlib.sha256((R/'10-generation'/a/'raw.png').read_bytes()).hexdigest()})
(O/'w-repair-bindings.json').write_text(json.dumps(rows,indent=2))

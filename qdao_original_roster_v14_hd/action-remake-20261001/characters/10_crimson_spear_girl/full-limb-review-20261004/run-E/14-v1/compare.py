from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
w=Path(__file__).parent;root=w.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=w/'native.png';im=Image.open(p);assert im.size==(1254,1254) and im.mode=='RGBA'
out=w/'review1024.png';im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8'))
derived={'file':out.relative_to(root).as_posix(),'sha256':sha(out),'width':1024,'height':1024,'mode':'RGBA','operation':'Whole1254 canvas resampled to1024 only; no translation/crop/bbox alignment','derivedFrom':{'file':p.relative_to(root).as_posix(),'sha256':sha(p),'generationRecord':str(p.relative_to(root))+'.generation.json'},'actualModel':None,'actualQuality':None}
Path(str(out)+'.generation.json').write_text(json.dumps(derived,indent=2),encoding='utf-8')
items=[('E13 current',root/'runtime/run/E/13.png'),('E14 original',root/'runtime/run/E/14.png'),('E14 corrected',out),('E15 current',root/'runtime/run/E/15.png')]
sheet=Image.new('RGB',(1800,780),(234,234,225));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for i,(label,f) in enumerate(items):
 z=Image.open(f).convert('RGBA');full=z.resize((450,450),Image.Resampling.LANCZOS);sheet.paste(full,(i*450,30),full)
 crop=z.crop((320,650,760,945));sheet.paste(crop,(i*450+5,480),crop)
 draw.text((i*450+10,4),label,font=font,fill='black')
sheet.save(w/'before-after.jpg',quality=95)
print(json.dumps({'nativeSHA256':sha(p),'nativeSize':list(im.size),'alphaRange':im.getchannel('A').getextrema(),'derivedSHA256':sha(out)}))


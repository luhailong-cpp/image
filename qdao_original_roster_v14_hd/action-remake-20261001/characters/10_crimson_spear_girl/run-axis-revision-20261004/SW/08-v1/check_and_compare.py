from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
w=Path(__file__).parent
root=w.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[('SW07 current',root/'runtime/run/SW/07.png'),('SW08 before',root/'runtime/run/SW/08.png'),('SW08 corrected',w/'review1024.png'),('SW09 current',root/'runtime/run/SW/09.png')]
out=Image.new('RGB',(1800,800),(233,232,222))
d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
sources=[]
for i,(label,p) in enumerate(rows):
 im=Image.open(p).convert('RGBA');x=i*450
 full=im.resize((450,450),Image.Resampling.LANCZOS);out.paste(full,(x,30),full)
 crop=im.crop((325,680,675,970)).resize((350,290),Image.Resampling.LANCZOS);out.paste(crop,(x+50,495),crop)
 d.text((x+10,5),label,fill='black',font=font)
 d.line((x,0,x,800),fill=(150,150,150))
 sources.append({'file':p.relative_to(root).as_posix(),'sha256':sha(p)})
out.save(w/'before-after.jpg',quality=95)
(w/'before-after.jpg.generation.json').write_text(json.dumps({'operation':'Visual audit montage only: whole-canvas resample and fixed lower-leg crops, no asset pose manipulation','derivedFrom':sources},indent=2),encoding='utf-8')
native=w/'native.png';im=Image.open(native);alpha=im.getchannel('A')
edges=[alpha.crop((0,0,im.width,1)),alpha.crop((0,im.height-1,im.width,im.height)),alpha.crop((0,0,1,im.height)),alpha.crop((im.width-1,0,im.width,im.height))]
assert im.mode=='RGBA' and im.size==(1254,1254)
assert alpha.getextrema()==(0,255) and max(e.getextrema()[1] for e in edges)==0
unique=all(sha(native)!=sha(p) for dr in ['SE','SW'] for p in (root/f'runtime/run/{dr}').glob('*.png'))
assert unique
check={'status':'technical-pass-visual-review-next','nativeSHA256':sha(native),'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':list(alpha.getextrema()),'edgeAlphaMax':0,'newSourceUnique':True,'frameMs':75,'frameCount':16,'referenceSources':sources}
(w/'technical-check.json').write_text(json.dumps(check,indent=2),encoding='utf-8')
print(json.dumps(check))


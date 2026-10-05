from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,sys
B=Path(__file__).resolve().parents[2]
key=sys.argv[1]
p=B/'staging'/f'{key}.png'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(im):
 a=im.getchannel('A'); m=a.point(lambda x:255 if x>128 else 0)
 return {'size':list(im.size),'bbox':m.getbbox(),'edgeAlphaAbove128':{'left':sum(x>128 for x in a.crop((0,0,1,im.height)).getdata()),'right':sum(x>128 for x in a.crop((im.width-1,0,im.width,im.height)).getdata()),'top':sum(x>128 for x in a.crop((0,0,im.width,1)).getdata()),'bottom':sum(x>128 for x in a.crop((0,im.height-1,im.width,im.height)).getdata())}}
im=Image.open(p); origmode=im.mode; im=im.convert('RGBA')
m={'key':key,'sha256':sha(p),'nativeMode':origmode,'native':metrics(im),'fullCanvas1024':metrics(im.resize((1024,1024),Image.Resampling.LANCZOS))}
out=B/'review'/'torso-continuity-E-20261005';out.mkdir(parents=True,exist_ok=True)
(out/f'{key}.metrics.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=p.with_suffix('.png.generation.json'); d=json.loads(record.read_text(encoding='utf-8'))
inputs=json.loads((B/'provenance'/f'{key}.input-hashes.json').read_text(encoding='utf-8-sig'))
d['evidence']['toolResultFile']=f'provenance/{key}.tool-result.json'
d['evidence']['inputHashesFile']=f'provenance/{key}.input-hashes.json'
d['evidence']['sourceGenerationRecord']=inputs['sourceGenerationRecord']
d['references']=inputs['references'];d['validation']=m
record.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frame=key.split('-')[2]
paths=[('E'+frame+' before',B/f'runtime/run/E/{frame}.png'),(key,p),('E05 baseline',B/'staging/run-E-05-v5.png'),('E12 baseline',B/'runtime/run/E/12.png')]
if key.split('-')[1]=='W':
 paths=[('W02',B/'runtime/run/W/02.png'),('W03 before',B/'runtime/run/W/03.png'),(key,p),('W04',B/'runtime/run/W/04.png')]
sheet=Image.new('RGB',(4*320,355),(47,52,57)); draw=ImageDraw.Draw(sheet)
for i,(label,fp) in enumerate(paths):
 q=Image.open(fp).convert('RGBA');q=q.resize((320,320),Image.Resampling.LANCZOS)
 sheet.paste(q,(i*320,28),q);draw.text((i*320+8,8),label,fill='white')
sheet.save(out/f'{key}.comparison.jpg',quality=95)
print(json.dumps(m))

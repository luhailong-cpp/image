from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,hashlib
b=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
key=sys.argv[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(im):
 a=im.getchannel('A');w,h=im.size
 count=lambda box:sum(x>128 for x in a.crop(box).getdata())
 return {'size':list(im.size),'mode':im.mode,'alphaGt128Bbox':a.point(lambda x:255 if x>128 else 0).getbbox(),'alphaGt128EdgePixels':{'top':count((0,0,w,1)),'right':count((w-1,0,w,h)),'bottom':count((0,h-1,w,h)),'left':count((0,0,1,h))}}
p=b/'staging'/f'{key}.png';im=Image.open(p);im.load();norm=im.resize((1024,1024),Image.Resampling.LANCZOS)
rp=p.with_suffix('.png.generation.json');r=json.loads(rp.read_text(encoding='utf-8'))
r['evidence']['toolResultFile']=f'provenance/{key}.tool-result.json'
r['evidence']['inputHashesFile']=f'provenance/{key}.input-hashes.json'
r['validation']={'native':metrics(im),'fullCanvas1024Lanczos':metrics(norm),'operation':'read-only in-memory full-canvas normalization; original PNG unchanged'}
r['sourceChain']=json.loads((b/f'provenance/{key}.input-hashes.json').read_text(encoding='utf-8'))
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frames=[('N15','runtime/run/N/15.png'),('old N16','runtime/run/N/16.png'),('N16 v6','staging/run-N-16-v6.png'),(key,f'staging/{key}.png'),('N01','runtime/run/N/01.png')]
for mode in ['full240','legs']:
 w,h=(240,265) if mode=='full240' else (330,325)
 sheet=Image.new('RGB',(w*len(frames),h),(225,228,228));d=ImageDraw.Draw(sheet)
 for i,(label,file) in enumerate(frames):
  src=Image.open(b/file).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
  if mode=='legs':src=src.crop((280,610,820,1024))
  src.thumbnail((w,h-25),Image.Resampling.LANCZOS)
  sheet.paste(src,(i*w+(w-src.width)//2,25),src);d.text((i*w+8,7),label,fill='#111111')
 sheet.save(out/f'{key}-{mode}.png')
print(json.dumps({'key':key,'sha256':sha(p),**r['validation']},indent=2))

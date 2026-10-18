from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent;Z=T.parent;R=T/'review/resume-20261016'
R.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
P=read(T/'progress.json');C=Path(P['candidate']);im=Image.open(C).convert('RGB');items=[]
def save(label,out,scope,box=None):
 p=R/(label+'.png');assert not p.exists();out.save(p);items.append({'label':label,'path':str(p),'sha256':sha(p),'size':list(out.size),'scope':scope,'box':box,'resized':False})
for axis in 'xy':
 for n in (1024,2048,3072):
  for q in range(4):
   b=(n-192,q*1024,n+192,(q+1)*1024) if axis=='x' else (q*1024,n-192,(q+1)*1024,n+192)
   save(f'{axis}{n}-q{q}',im.crop(b),'internal seam',b)
for q in range(4):
 b=(3712,q*1024,4096,(q+1)*1024);save(f'east-q{q}',im.crop(b),'east core edge evidence',b)
 b=(q*1024,3712,(q+1)*1024,4096);save(f'south-q{q}',im.crop(b),'south canvas outer edge',b)
neighbors={}
for direction,tile in [('north','r15_c15'),('west','r16_c14')]:
 p=Path(read(Z/tile/'progress.json')['candidate']);adj=Image.open(p).convert('RGB');neighbors[direction]={'path':str(p),'sha256':sha(p)}
 for q in range(4):
  if direction=='north':
   a=adj.crop((q*1024,3904,(q+1)*1024,4096));b=im.crop((q*1024,0,(q+1)*1024,192));out=Image.new('RGB',(1024,384));out.paste(a,(0,0));out.paste(b,(0,192))
  else:
   a=adj.crop((3904,q*1024,4096,(q+1)*1024));b=im.crop((0,q*1024,192,(q+1)*1024));out=Image.new('RGB',(384,1024));out.paste(a,(0,0));out.paste(b,(192,0))
  save(f'{direction}-pair-q{q}',out,'real core pair, join at 192')
e={'candidate':{'path':str(C),'sha256':sha(C)},'context':{'path':P['context'],'sha256':sha(Path(P['context']))},'neighbors':neighbors,'images':items,'status':'pending_visual_QA','formalAccepted':False}
(R/'evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'candidate':e['candidate'],'context':e['context'],'directory':str(R),'crops':len(items)}))

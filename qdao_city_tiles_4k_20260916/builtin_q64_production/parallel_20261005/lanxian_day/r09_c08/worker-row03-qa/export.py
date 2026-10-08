from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,sys
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
T=ROOT/'r09_c08'; col=int(sys.argv[1]);assert 1<=col<=3
cell=f'r03_c{col:02d}';D=T/'worker-row03-qa'/cell
assert not D.exists();D.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(row,col):
 p=T/'native'/f'r{row:02d}_c{col:02d}.png';g=Path(str(p)+'.generation.json');r=json.loads(g.read_text(encoding='utf-8-sig'))
 assert sha(p)==r['sha256']
 return p,Image.open(p).convert('RGB'),g
own,O,og=source(3,col);north,N,ng=source(2,col);east,E,eg=source(3,col+1)
out=[]
for kind,size,pieces in [
 ('north-join1024x512',(1024,512),[(north,N,ng,(115,883,1139,1139),(0,0)),(own,O,og,(115,115,1139,371),(0,256))]),
 ('east-join512x1024',(512,1024),[(own,O,og,(883,115,1139,1139),(0,0)),(east,E,eg,(115,115,371,1139),(256,0))])]:
 canvas=Image.new('RGB',size);maps=[]
 for p,im,g,box,xy in pieces:
  crop=im.crop(box);canvas.paste(crop,xy)
  maps.append({'file':str(p),'sha256':sha(p),'generationRecord':str(g),'generationRecordSha256':sha(g),'sourceBox':list(box),'destinationXY':list(xy),'rawRGBSha256':hashlib.sha256(crop.tobytes()).hexdigest()})
 dest=D/(kind+'.png');canvas.save(dest)
 out.append({'file':str(dest),'sha256':sha(dest),'pixels':list(size),'rawRGBSha256':hashlib.sha256(canvas.tobytes()).hexdigest(),'pixelMappings':maps,'resampling':'none','actualVisualReviewPending':True})
m={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'cell':cell,'purpose':'Exact original-pixel neighbor core joins for row3 continuation','scopes':out,'finalArt':False}
(D/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'dir':str(D),'scopes':out}))


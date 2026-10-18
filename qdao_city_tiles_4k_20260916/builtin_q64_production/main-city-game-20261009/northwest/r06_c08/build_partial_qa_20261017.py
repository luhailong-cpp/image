from pathlib import Path
import sys,hashlib
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
Q=T/'qa/partial15-restart-20261017';assert not (Q/'manifest.json').exists();Q.mkdir(exist_ok=True)
sel=p.read(T/'selection.json');cores={k:Image.open(v).convert('RGB').crop((115,115,1139,1139)) for k,v in sel.items()}
refs={k:dict(file=v,sha256=p.sha(v)) for k,v in sel.items()}
def rgb(im):return hashlib.sha256(im.tobytes()).hexdigest()
prior={}
for f in (T/'qa/source-review').glob('*/review.json'):
 r=p.read(f)
 if not r.get('actuallyViewed'):continue
 for c in r.get('cropReviews',[]):
  if c['status'] not in ['passed','needs_repair']:continue
  ff=Path(c['file'])
  if not ff.exists() or not c.get('sha256') or p.sha(ff)!=c['sha256']:continue
  prior.setdefault(rgb(Image.open(ff).convert('RGB')),[]).append(dict(file=str(f),status=c['status'],finding=c.get('finding',r.get('finding')),actuallyViewed=True,cropFile=str(ff),cropSha256=c['sha256']))
crops=[]
def save(name,parts,size):
 if not all(k in cores for k,b,xy in parts):return
 im=Image.new('RGB',size)
 for k,b,xy in parts:im.paste(cores[k].crop(b),xy)
 f=Q/(name+'.png');p.save_png(f,im);h=rgb(im)
 crops.append(dict(name=name,file=str(f),sha256=p.sha(f),rgbPixelSHA256=h,sourceReferences={k:refs[k] for k,b,xy in parts},matchingPriorReviews=prior.get(h,[]),actuallyViewed=False,status='unreviewed'))
for r in range(1,5):
 for c in range(1,4):
  save(f'internal_x{c*1024}_seg{r}',[(f's{r:02}_{c:02}',(864,0,1024,1024),(0,0)),(f's{r:02}_{c+1:02}',(0,0,160,1024),(160,0))],(320,1024))
for r in range(1,4):
 for c in range(1,5):
  save(f'internal_y{r*1024}_seg{c}',[(f's{r:02}_{c:02}',(0,864,1024,1024),(0,0)),(f's{r+1:02}_{c:02}',(0,0,1024,160),(0,160))],(1024,320))
for r in range(1,4):
 for c in range(1,4):
  save(f'internal_jx{c*1024}_y{r*1024}',[(f's{r:02}_{c:02}',(864,864,1024,1024),(0,0)),(f's{r:02}_{c+1:02}',(0,864,160,1024),(160,0)),(f's{r+1:02}_{c:02}',(864,0,1024,160),(0,160)),(f's{r+1:02}_{c+1:02}',(0,0,160,160),(160,160))],(320,320))
p.write_json(Q/'manifest.json',dict(tile='r06_c08',selectedCount=len(sel),selectedHashes=refs,notACompleteCandidate=True,coreMissing=['s01_04'],nativePixelScale=1,crops=crops,formalAccepted=False),replace=False)
print({'count':len(crops),'reusable':sum(bool(c['matchingPriorReviews']) for c in crops),'new':[c['name'] for c in crops if not c['matchingPriorReviews']]})


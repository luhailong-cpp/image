from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z))
import production_v2 as p
def rgbhash(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
def ref(f):return dict(file=str(f),sha256=p.sha(f))
tag=sys.argv[1]
C=T/'candidate'/tag;Q=T/'qa'/tag
assert not C.exists() and not Q.exists()
coords=p.coordinates('r06_c08')['patches'];sel=p.read(T/'selection.json')
assert len(sel)==16 and set(sel)=={x['id'] for x in coords}
image=Image.new('RGB',(4096,4096));index=np.zeros((4096,4096),dtype=np.uint8);sources=[]
for i,c in enumerate(coords,1):
 f=Path(sel[c['id']]);v=p.validate_native(f,T,c['id']);core=Image.open(f).convert('RGB').crop((115,115,1139,1139));x=(int(c['id'][4:6])-1)*1024;y=(int(c['id'][1:3])-1)*1024
 image.paste(core,(x,y));index[y:y+1024,x:x+1024]=i;sources.append(dict(ref(f),index=i,patch=c['id'],sourceCoreLTRB=[115,115,1139,1139],destinationLTRB=[x,y,x+1024,y+1024],coreWorldBox=c['coreWorldBox'],validation=v))
C.mkdir(parents=True);Q.mkdir(parents=True);f=C/'candidate.png';p.save_png(f,image);ip=C/'source-index.png';p.save_png(ip,Image.fromarray(index));arr=np.array(Image.open(f).convert('RGB'));idx=np.array(Image.open(ip));proof=[]
for a in sources:
 x,y,x1,y1=a['destinationLTRB'];src=np.array(Image.open(a['file']).convert('RGB'))[115:1139,115:1139];ok=bool(np.array_equal(arr[y:y1,x:x1],src));iok=bool(np.all(idx[y:y1,x:x1]==a['index']));assert ok and iok;proof.append(dict(patch=a['patch'],pixelCount=1024*1024,sourcePixelsEqual=ok,sourceIndexEqual=iok))
manifest=dict(tile='r06_c08',candidate=ref(f),sourceIndex=ref(ip),worldBox=p.tile_box('r06_c08'),size=[4096,4096],sourceCount=16,sources=sources,sameWorldNativeCopy=True,resampled=False,feathered=False,colorAdjusted=False,pixelProof=dict(totalPixels=4096*4096,allPixelsAccountedFor=True,checks=proof),internalQAPassed=False,formalAccepted=False)
p.write_json(C/'manifest.json',manifest,replace=False)
prior={}
for rf in sorted((T/'qa/source-review').glob('*/review.json')):
 r=p.read(rf)
 if not r.get('actuallyViewed'):continue
 for a in r.get('cropReviews',[]):
  ff=Path(a['file'])
  if not ff.exists() or (a.get('sha256') and p.sha(ff)!=a['sha256']):continue
  prior.setdefault(rgbhash(Image.open(ff)),[]).append(dict(reviewFile=str(rf),file=str(ff),sha256=p.sha(ff),status=a['status'],actuallyViewed=True,finding=a.get('finding',r.get('finding'))))
crops=[]
def save(name,im,kind,box=None,provenance=None):
 ff=Q/(name+'.png');p.save_png(ff,im);rh=rgbhash(im);crops.append(dict(ref(ff),name=name,kind=kind,size=list(im.size),nativePixelScale=1,rgbPixelSHA256=rh,candidateLTRB=box,provenance=provenance,matchingPriorReviews=prior.get(rh,[]),actuallyViewed=False,status='unreviewed'))
for x in [1024,2048,3072]:
 for r in range(4):
  b=[x-160,r*1024,x+160,(r+1)*1024];save(f'internal_x{x}_seg{r+1}',image.crop(b),'internal',b)
for y in [1024,2048,3072]:
 for c in range(4):
  b=[c*1024,y-160,(c+1)*1024,y+160];save(f'internal_y{y}_seg{c+1}',image.crop(b),'internal',b)
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:
  b=[x-160,y-160,x+160,y+160];save(f'internal_jx{x}_y{y}',image.crop(b),'internal',b)
W=Z/'r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png';assert p.sha(W)=='e3184ae204d0cd8f0ea701bf6b3281449bb1489c18514f525869f37d72326609';wi=Image.open(W).convert('RGB')
for r in range(4):
 im=Image.new('RGB',(320,1024));im.paste(wi.crop((3936,r*1024,4096,(r+1)*1024)),(0,0));im.paste(image.crop((0,r*1024,160,(r+1)*1024)),(160,0));save(f'west_seg{r+1}',im,'external',provenance=ref(W))
for y in [1024,2048,3072]:
 im=Image.new('RGB',(320,320));im.paste(wi.crop((3936,y-160,4096,y+160)),(0,0));im.paste(image.crop((0,y-160,160,y+160)),(160,0));save(f'west_joint{y}',im,'external',provenance=ref(W))
N=Z/'r05_c08';ns=p.read(N/'selection.json');north={};northrefs={}
for c in range(1,5):
 pid=f's04_{c:02}';ff=Path(ns[pid]) if pid in ns else None
 if ff and ff.exists():
  p.validate_native(ff,N,pid);north[c]=Image.open(ff).convert('RGB').crop((115,115,1139,1139));northrefs[c]=ref(ff)
  im=Image.new('RGB',(1024,320));im.paste(north[c].crop((0,864,1024,1024)),(0,0));im.paste(image.crop(((c-1)*1024,0,c*1024,160)),(0,160));save(f'north_seg{c}',im,'external',provenance=northrefs[c])
for c in range(1,4):
 if c in north and c+1 in north:
  im=Image.new('RGB',(320,320));im.paste(north[c].crop((864,864,1024,1024)),(0,0));im.paste(north[c+1].crop((0,864,160,1024)),(160,0));im.paste(image.crop((c*1024-160,0,c*1024+160,160)),(0,160));save(f'north_joint{c*1024}',im,'external',provenance=[northrefs[c],northrefs[c+1]])
p.write_json(Q/'manifest.json',dict(candidate=ref(f),candidateManifest=str(C/'manifest.json'),crops=crops,internalCount=33,externalCount=len(crops)-33,unavailableExternal=dict(northMissingSegments=[c for c in range(1,5) if c not in north],east='unavailable',south='unavailable'),formalAccepted=False),replace=False)
print(json.dumps(dict(candidate=ref(f),manifest=str(Q/'manifest.json'),cropCount=len(crops),reusable=sum(bool(c['matchingPriorReviews']) for c in crops),new=[c['name'] for c in crops if not c['matchingPriorReviews']])))

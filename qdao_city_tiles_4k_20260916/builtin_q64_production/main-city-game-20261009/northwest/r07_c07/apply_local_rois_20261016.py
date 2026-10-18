from pathlib import Path
import json,hashlib,sys
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def ph(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
def write(f,o):f.parent.mkdir(parents=True,exist_ok=True);assert not f.exists();f.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
base=T/'candidate/hard-native16-20261016-d2798e0634074d26';old=read(base/'provenance.json');im=Image.open(base/'candidate.png').convert('RGB')
ops=[('jamb3072_fix01',[115,480,360,740]),('jamb2048_fix01',[330,535,495,720]),('stone1024_fix01',[245,520,1139,730])]
variant='native19-local-repairs-20261016-v1'
if len(sys.argv)>1 and sys.argv[1]=='north20':
 ops.append(('north-right_fix02',[505,115,900,450]))
 variant='native20-local-repairs-20261016-v1'
D=T/'candidate'/variant;Q=T/'qa'/D.name;D.mkdir(parents=True,exist_ok=False);Q.mkdir(parents=True,exist_ok=False)
idx=np.zeros((4096,4096),dtype=np.uint8);srcs=[]
for n,s in enumerate(old['nativeSources'],1):
 x,y,r,b=s['destination'];idx[y:b,x:r]=n
 srcs.append(dict(s,sourceIndex=n,sourceTileOffset=[s['destination'][0]-115,s['destination'][1]-115]))
for name,b in ops:
 d=T/'repairs'/name;g=read(d/'generation.json');assert sha(d/'native.png')==g['sha256'];der=read(d/'input.derivation.json');o=der['tileLocalBox'][:2];dest=[b[0]+o[0],b[1]+o[1],b[2]+o[0],b[3]+o[1]];assert min(dest)>=0 and max(dest)<=4096
 n=len(srcs)+1;im.paste(Image.open(d/'native.png').convert('RGB').crop(b),dest[:2]);x,y,r,z=dest;idx[y:z,x:r]=n
 srcs.append(dict(id=name,sourceIndex=n,file=g['file'],sha256=g['sha256'],generationRecord=str(d/'generation.json'),crop=b,destination=dest,sourceTileOffset=o,resampled=False))
out=D/'candidate.png';im.save(out);Image.fromarray(idx).save(D/'source-index.png');a=np.asarray(im)
counts={}
for s in srcs:
 v=np.asarray(Image.open(s['file']).convert('RGB'));ys,xs=np.where(idx==s['sourceIndex']);ox,oy=s['sourceTileOffset']
 assert np.array_equal(a[ys,xs],v[ys-oy,xs-ox]);counts[s['id']]=len(xs)
assert sum(counts.values())==4096**2
write(D/'provenance.json',dict(output=dict(file=str(out),sha256=sha(out),size=[4096,4096]),base=old['output'],nativeSources=srcs,sourcePixelCounts=counts,sourceIndex=dict(file=str(D/'source-index.png'),sha256=sha(D/'source-index.png')),byteExactSourcePixels=4096**2,allPixelsVerified=True,sourceResampled=False,sourceUpscaled=False,operation='hard same-world native ROI substitution; binary ownership, no blending or painting',formalAccepted=False))
oldm=read(T/'qa'/base.name/'manifest.json');crops=[]
for c in oldm['crops']:
 name=c['name'];b=c['tileBox']
 if b:ci=im.crop(b)
 else:
  side='north' if name.startswith('north') else 'west';nb=Image.open(oldm['neighbors'][side]['file']).convert('RGB')
  if '_seg' in name:
   k=int(name.rsplit('seg',1)[1])-1
   if side=='north':ci=Image.new('RGB',(1024,320));ci.paste(nb.crop((k*1024,3936,(k+1)*1024,4096)),(0,0));ci.paste(im.crop((k*1024,0,(k+1)*1024,160)),(0,160))
   else:ci=Image.new('RGB',(320,1024));ci.paste(nb.crop((3936,k*1024,4096,(k+1)*1024)),(0,0));ci.paste(im.crop((0,k*1024,160,(k+1)*1024)),(160,0))
  else:
   k=int(name.rsplit('joint',1)[1]);ci=Image.new('RGB',(320,320))
   if side=='north':ci.paste(nb.crop((k-160,3936,k+160,4096)),(0,0));ci.paste(im.crop((k-160,0,k+160,160)),(0,160))
   else:ci.paste(nb.crop((3936,k-160,4096,k+160)),(0,0));ci.paste(im.crop((0,k-160,160,k+160)),(160,0))
 f=Q/(name+'.png');ci.save(f);same=ph(ci)==c['pixelSha256'];crops.append(dict(name=name,file=str(f),sha256=sha(f),pixelSha256=ph(ci),kind=c['kind'],tileBox=b,nativePixelScale=1,identicalToBaseCrop=same,baseCrop=dict(file=c['file'],sha256=c['sha256']),status='reuse_base_review' if same else 'needs_review'))
bounds=[]
for s in srcs[16:]:
 x,y,r,b=s['destination'];box=[max(0,x-100),max(0,y-100),min(4096,r+100),min(4096,b+100)];ci=im.crop(box);f=Q/(s['id']+'-roi-surround.png');ci.save(f)
 bounds.append(dict(name=s['id'],file=str(f),sha256=sha(f),tileBox=box,adoptedROI=s['destination'],nativePixelScale=1,actuallyViewed=False))
write(Q/'manifest.json',dict(candidate=dict(file=str(out),sha256=sha(out)),internalCount=33,externalCount=14,crops=crops,roiBoundaryCrops=bounds,unchangedCropCount=sum(c['identicalToBaseCrop'] for c in crops),formalAccepted=False))
print(json.dumps(dict(candidate=str(out),sha256=sha(out),qa=str(Q),unchangedCropCount=sum(c['identicalToBaseCrop'] for c in crops),changed=[c['name'] for c in crops if not c['identicalToBaseCrop']],sourcePixels=counts)))


from pathlib import Path
from datetime import datetime,timezone
import sys,hashlib,numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');Z=T.parent;sys.path.insert(0,str(Z));import production_v2 as p
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08/repair-batches/blue-glaze-cross-20261017-fix03');tag='native17-glaze-repair-20261017-v1';C=T/'candidate'/tag;Q=T/'qa'/tag;assert not C.exists() and not Q.exists();C.mkdir();Q.mkdir()
base=T/'candidate/native16-restart-20261017-v1';bm=p.read(base/'manifest.json');trial=p.read(B/'trial-v1.json')
assert p.sha(base/'candidate.png')==trial['baseSha256'];assert p.sha(B/'native.png')==trial['sourceSha256']
a=np.array(Image.open(base/'candidate.png').convert('RGB'));idx=np.array(Image.open(base/'source-index.png'));s=np.array(Image.open(B/'native.png').convert('RGB'));ma=np.array(Image.open(B/'mask-v1.png'))>0
yy,xx=np.where(ma);tx=xx-160;ty=yy+1421;a[ty,tx]=s[yy,xx];idx[ty,tx]=17;im=Image.fromarray(a);p.save_png(C/'candidate.png',im);p.save_png(C/'source-index.png',Image.fromarray(idx))
sources=bm['sources']+[dict(index=17,file=str(B/'native.png'),sha256=p.sha(B/'native.png'),worldBox=[28512,21901,29766,23155],tileOrigin=[-160,1421],generationRecord=str(B/'generation.json'),mask=str(B/'mask-v1.png'),maskSha256=p.sha(B/'mask-v1.png'))]
proof=[];total=0
for item in sources:
 owner=item['index'];iy,ix=np.where(idx==owner);src=np.array(Image.open(item['file']).convert('RGB'))
 if owner==17:sx=ix+160;sy=iy-1421
 else:
  x,y,x1,y1=item['destinationLTRB'];sx=ix-x+115;sy=iy-y+115
 assert np.array_equal(a[iy,ix],src[sy,sx]);total+=len(ix);proof.append(dict(index=owner,pixelCount=len(ix),sameWorldNativePixelsEqual=True,sourceSha256=item['sha256']))
assert total==4096*4096 and np.array_equal(a,np.array(Image.open(B/'trial-v1.png').convert('RGB')))
def ref(f):return dict(file=str(f),sha256=p.sha(f))
p.write_json(C/'manifest.json',dict(tile='r06_c08',candidate=ref(C/'candidate.png'),sourceIndex=ref(C/'source-index.png'),worldBox=p.tile_box('r06_c08'),size=[4096,4096],selectedCoreCount=16,sourceCount=17,sources=sources,sameWorldNativeCopy=True,resampled=False,feathered=False,colorAdjusted=False,pixelProof=dict(totalPixels=total,allPixelsAccountedFor=True,checks=proof),baseCandidate=bm['candidate'],repair=ref(B/'trial-v1.json'),internalQAPassed=False,formalAccepted=False),replace=False)
oldq=T/'qa/native16-restart-20261017-v1';qm=p.read(oldq/'manifest.json');qr=p.read(oldq/'reviewed-status.json');reviews={c['name']:c for c in qr['cropReviews']};crops=[];changed=[]
W=Image.open(Z/'r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png').convert('RGB')
for c in qm['crops']:
 name=c['name'];old=Image.open(c['file']).convert('RGB')
 if c['kind']=='internal':new=im.crop(c['candidateLTRB'])
 elif name.startswith('west_'):
  if 'seg' in name:y0=(int(name.split('seg')[1])-1)*1024;y1=y0+1024
  else:y=int(name.split('joint')[1]);y0=y-160;y1=y+160
  new=Image.new('RGB',(320,y1-y0));new.paste(W.crop((3936,y0,4096,y1)),(0,0));new.paste(im.crop((0,y0,160,y1)),(160,0))
 else:new=old
 rh=hashlib.sha256(new.tobytes()).hexdigest();same=new.size==old.size and new.tobytes()==old.tobytes()
 out=dict(c,candidate=ref(C/'candidate.png'),rgbPixelSHA256=rh)
 if same:
  out.update(status=reviews[name]['status'],actuallyViewed=False,reusedPixelIdentical=True,reusedReview=dict(file=str(oldq/'reviewed-status.json'),sha256=p.sha(oldq/'reviewed-status.json'),crop=reviews[name]))
 else:
  f=Q/(name+'.png');p.save_png(f,new);out.update(ref(f));out.update(status='unreviewed',actuallyViewed=False,reusedPixelIdentical=False);changed.append(name)
 crops.append(out)
p.write_json(Q/'manifest.json',dict(candidate=ref(C/'candidate.png'),candidateManifest=str(C/'manifest.json'),crops=crops,internalCount=33,externalCount=9,changed=changed,reusedCount=sum(c['reusedPixelIdentical'] for c in crops),unavailableExternal=qm['unavailableExternal'],internalQAPassed=False,formalAccepted=False),replace=False)
print(dict(candidate=ref(C/'candidate.png'),pixelTotal=total,changed=changed))


from pathlib import Path
from PIL import Image
import numpy as np,sys
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
def a(f):return np.asarray(Image.open(f).convert('RGB'))
D=R/'joint-v5';D.mkdir(exist_ok=True)
old=a(R/'references/w-wood-return-input.png');new=a(R/'native/w-wood-return.png')
yy,xx=np.mgrid[:1254,:1254];alpha=np.clip(np.minimum(np.minimum(xx-154,642-xx),np.minimum(yy-465,660-yy))/32,0,1)
combined=np.rint(old*(1-alpha[:,:,None])+new*alpha[:,:,None]).astype(np.uint8)
f=D/'wood-return-final-composite.png';Image.fromarray(combined).save(f);np.savez_compressed(D/'wood-alpha.npz',alpha=alpha)
p.derived(f,[R/'references/w-wood-return-input.png',R/'native/w-wood-return.png'],{'method':'native coordinate tiny pigment-band AI patch, bounded alpha32; no image scaling or blur','rectLTRB':[154,465,643,661],'mask':str(D/'wood-alpha.npz'),'formalAccepted':False})
record=p.read(R/'joint-v4/integration.json');tile='r10_c13';entry=record['outputs'][tile]
im=a(entry['file']).copy();roi=im[1470:2724,3072:4096];mask=np.any(combined[:,:1024]!=old[:,:1024],axis=2)
assert np.array_equal(roi,old[:,:1024]);roi[mask]=combined[:,:1024][mask]
dest=D/f'{tile}-candidate.png';Image.fromarray(im).save(dest)
base=a(entry['base']);allmask=np.any(im!=base,axis=2);mf=D/f'{tile}-change-mask.png';Image.fromarray(allmask.astype(np.uint8)*255).save(mf)
p.derived(dest,[entry['file'],f],{'method':'exact changed native ROI into r10_c13','mask':str(mf),'formalAccepted':False})
record['outputs'][tile].update({'file':str(dest),'sha256':p.sha(dest),'mask':str(mf),'maskSha256':p.sha(mf),'changedPixels':int(allmask.sum())})
record['createdAt']=p.stamp();record['woodReturn']={'file':str(f),'sha256':p.sha(f),'pixelsChanged':int(mask.sum())};p.write(D/'integration.json',record)
print(p.sha(dest))


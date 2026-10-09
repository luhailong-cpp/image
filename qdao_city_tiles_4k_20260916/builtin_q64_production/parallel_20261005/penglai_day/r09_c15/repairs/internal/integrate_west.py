import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
import ai_helper as h
import quilt as q
O=h.O;sha=h.sha;derived=h.derived;smooth=q.smooth
def cut(cost,a,b):
 c=cost[:,a:b];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.3,dp,np.r_[dp[1:],1e12]+.3]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+np.min(z,axis=0)
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+a


def join(a,b,label):
 h,w,_=a.shape
 # Rotate overlap to the same native vertical-ownership orientation, then restore.
 aa=np.transpose(a,(1,0,2));bb=np.transpose(b,(1,0,2));n,ww,_=aa.shape
 f=np.clip(smooth(aa-bb)/2,-12,12);fade=np.minimum(1,np.minimum(np.arange(ww),np.arange(ww)[::-1])/48)[None,:,None];fa=-f*fade;fb=f*fade;ac=aa+fa;bc=bb+fb
 cost=np.sqrt(np.mean((ac-bc)**2,axis=2))+.6*np.mean(abs(np.diff(aa,axis=1,prepend=aa[:,:1])-np.diff(bb,axis=1,prepend=bb[:,:1])),axis=2)
 path=cut(cost,35,ww-35);own=np.arange(ww)[None,:]<path[:,None];out=np.transpose(np.where(own[:,:,None],ac,bc),(1,0,2))
 fp=O/(label+'-fields.npz');np.savez_compressed(fp,path=path,fieldA=fa,fieldB=fb,ownerA=own)
 mp=O/(label+'-owner-a.png');Image.fromarray((own.T*255).astype('uint8')).save(mp);derived(mp,[O/f'west{i}-ai-v1-generated.png' for i in [1,2,3,4]],{'method':'native binary overlap quilt','fieldFile':str(fp),'fieldSha256':sha(fp),'capPerSide':12,'imageBlur':False,'resample':False,'fieldOnlySmoothing':49})
 return out,mp

def runv2():
 ys=[0,1024,2048,2842];native=[O/f'west{i}-ai-v1-generated.png' for i in range(1,5)];a=np.zeros((4096,1254,3),np.float32);a[:1254]=np.asarray(Image.open(native[0]),np.float32);prevend=1254;owners=[]
 for y,p in zip(ys[1:],native[1:]):
  b=np.asarray(Image.open(p),np.float32);overlap=prevend-y;mix,mp=join(a[y:prevend],b[:overlap],f'west-v1-rowjoin-{y}');a[y:prevend]=mix;a[prevend:y+1254]=b[overlap:];prevend=y+1254;owners.append(mp)
 qp=O/'ai-strip-west-v1.png';Image.fromarray(np.clip(np.rint(a),0,255).astype('uint8')).save(qp);derived(qp,native+owners,{'method':'native overlap quilt with bounded color correction','scale':1})
 source=O/'west-joint-source.png';base=np.asarray(Image.open(source),np.float32);b=np.asarray(Image.open(qp),np.float32);cost=np.mean(np.minimum(abs(base-b),50)**2,axis=2)
 left=cut(cost,320,440);right=cut(cost,815,940);Y,X=np.indices((4096,1254));m=(X>=left[:,None])&(X<right[:,None]);border=m&(~np.roll(m,1,1)|~np.roll(m,-1,1));grad=np.max(abs(base-np.roll(base,1,0))+abs(base-np.roll(base,1,1)),axis=2);reliable=border&(grad<35)&(np.max(abs(base-b),axis=2)<35)
 weight=smooth(smooth(reliable[:,:,None].astype('float32')));num=smooth(smooth((base-b)*reliable[:,:,None]));f=np.clip(num/np.maximum(weight,1e-6),-12,12)*np.clip(weight*240,0,1)*m[:,:,None];rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.where(m[:,:,None],rep,base.astype('uint8'))
 fp=O/'west-v1-perimeter-fields.npz';np.savez_compressed(fp,left=left,right=right,field=f);rp=O/'joint-replacement-west-v1.png';mp=O/'joint-mask-west-v1.png';dest=O/'joint-candidate-west-v1.png';Image.fromarray(rep).save(rp);Image.fromarray((m*255).astype('uint8')).save(mp);Image.fromarray(out).save(dest)
 derived(mp,[source,qp],{'method':'single continuous left/right binary ownership over full native4096 height','ranges':{'left':[320,440],'right':[815,940]},'feather':False})
 derived(rp,[source,qp,mp],{'method':'bounded perimeter color correction','cap':12,'fieldFile':str(fp),'fieldSha256':sha(fp),'imageBlur':False,'resample':False,'fieldOnlySmoothing':'two49pxbox'})
 derived(dest,[source,rp,mp],{'method':'binary mask composition','outsideMaskIdentical':True,'resample':False})
 export(dest,mp,'west-v1')

def export(dest,mp,version):
 canvas=Image.open(dest).convert('RGB');allmask=Image.open(mp).convert('L');sources=json.loads((O/'west-sources.json').read_text(encoding='utf8'));tiles=[]
 for i,side in enumerate(['left','right']):
  base=Path(sources[i]['file']);tile=Image.open(base).convert('RGB');box=(0 if not i else 627,0,627 if not i else 1254,4096);tile.paste(canvas.crop(box),(3469 if not i else 0,0));p=O/(f'r09_c14-west-joint-candidate-{version}.png' if not i else f'r09_c15-west-joint-candidate-{version}.png');tile.save(p);derived(p,[base,dest,mp],{'method':'native exact replacement of shared strip','outsideMaskIdentical':True})
  tm=Image.new('L',(4096,4096));tm.paste(allmask.crop(box),(3469 if not i else 0,0));t=O/(side+f'-tile-mask-{version}.png');tm.save(t);derived(t,[mp],{'method':'place joint mask into corresponding tile','side':side});tiles.append({'side':side,'base':str(base),'baseSha256':sha(base),'candidate':str(p),'sha256':sha(p),'mask':str(t),'maskSha256':sha(t),'bbox':tm.getbbox()})
 for y in [0,1024,2048,2842]:
  p=O/f'qa-{version}-{y}.png';canvas.crop((0,y,1254,y+1254)).save(p);derived(p,[dest],{'nativeCrop':[0,y,1254,y+1254]})
 for y in [1139,2163,3072]:
  p=O/f'qa-{version}-return-{y}.png';canvas.crop((220,y-180,1034,y+180)).save(p);derived(p,[dest],{'nativeCrop':[220,y-180,1034,y+180]})

 (O/f'merge-manifest-{version}.json').write_text(json.dumps({'joint':str(dest),'sha256':sha(dest),'mask':str(mp),'maskSha256':sha(mp),'globalOriginXY':[56717,32768],'seamX':627,'tiles':tiles,'globalCornerPending':True,'formalAccepted':False},indent=2),encoding='utf8');print(json.dumps(tiles,indent=2))
if __name__=='__main__':runv2()

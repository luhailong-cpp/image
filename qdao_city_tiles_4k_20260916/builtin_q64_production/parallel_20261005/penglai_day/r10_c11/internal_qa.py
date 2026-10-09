from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));import helper as h
O=R/'repairs';O.mkdir(exist_ok=True)
def arr(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)
def smooth2(a,r):
 def dim(a,k):
  pad=[(0,0)]*a.ndim;pad[k]=(r,r);v=np.pad(a,pad,mode='edge');v=np.cumsum(v,axis=k,dtype=np.float64);z=np.zeros_like(np.take(v,[0],axis=k));v=np.concatenate([z,v],axis=k);i=[slice(None)]*a.ndim;j=i.copy();i[k]=slice(2*r+1,None);j[k]=slice(None,-2*r-1);return (v[tuple(i)]-v[tuple(j)])/(2*r+1)
 return dim(dim(a,0),1).astype(np.float32)
def path(cost):
 n,w=cost.shape;dp=cost[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  opts=np.stack([np.r_[np.inf,dp[:-1]],dp,np.r_[dp[1:],np.inf]])
  c=np.argmin(opts,axis=0);dp=opts[c,np.arange(w)]+cost[y];back[y]=c-1
 p=np.zeros(n,np.int16);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p

def qa(a,label,source):
 for axis in ['x','y']:
  for pos in [1024,2048,3072]:
   board=Image.new('RGB',(1024,1024))
   for k in range(4):
    crop=a.crop((pos-128,k*1024,pos+128,(k+1)*1024)) if axis=='x' else a.crop((k*1024,pos-128,(k+1)*1024,pos+128))
    if axis=='x':crop=crop.transpose(Image.Transpose.ROTATE_90)
    board.paste(crop,(0,k*256))
   d=R/'qa'/f'{label}-{axis}{pos}.png';board.save(d);h.p.derived(d,[source],{'method':'four native256x1024 seam strips, x strips rotated90'})
 b=Image.new('RGB',(960,960))
 for iy,y in enumerate([1024,2048,3072]):
  for ix,x in enumerate([1024,2048,3072]):b.paste(a.crop((x-160,y-160,x+160,y+160)),(ix*320,iy*320))
 f=R/'qa'/f'{label}-junctions.png';b.save(f);h.p.derived(f,[source],{'method':'nine native320x320 junction crops'})

def run():
 sources=[R/'native'/f'p{r}{c}.png' for r in [3,4] for c in [1,2]]
 a=np.concatenate([arr(p)[1024:1254,115:1139] for p in sources[:2]],axis=1);b=np.concatenate([arr(p)[:230,115:1139] for p in sources[2:]],axis=1)
 err=np.mean(abs(a-b),axis=2);ga=np.diff(a,axis=0,prepend=a[:1]);gb=np.diff(b,axis=0,prepend=b[:1]);cost=err+2*np.mean(abs(ga-gb),axis=2)+.2*(np.mean(abs(ga),axis=2)+np.mean(abs(gb),axis=2));cost[:50]=1e6;cost[180:]=1e6
 for x in range(2048):
  reach=min(x,2047-x,65);lo=max(50,115-reach);hi=min(180,116+reach);cost[:lo,x]=1e6;cost[hi:,x]=1e6
 pp=path(cost.T);yy=np.arange(230)[:,None];mask=yy>=pp[None,:];df=np.clip(smooth2(b-a,12),-16,16);dist=abs(yy-pp[None,:]);w=np.clip(1-dist/100,0,1)**2;edge=np.minimum(np.clip(np.arange(2048)/64,0,1),np.clip((2047-np.arange(2048))/64,0,1));w*=edge[None,:]
 af=.5*df*w[:,:,None];bf=-.5*df*w[:,:,None];out=np.where(mask[:,:,None],b+bf,a+af);out=np.clip(np.rint(out),0,255).astype('uint8')
 for name,v in [('rock-y3072-replacement-v1.png',out),('rock-y3072-source-choice-v1.png',mask.astype('uint8')*255)]:
  p=O/name;Image.fromarray(v).save(p);h.p.derived(p,sources,{'method':'native overlap source selection; paired boundedRGB fields only','nativeOriginTileXY':[0,2957],'newAI':False,'sourceChoiceMask':str(O/'rock-y3072-source-choice-v1.png'),'geometricShift':0,'resampling':False,'imageBlur':False,'imageFeather':False,'fieldCapPerSide':8})
 np.savez_compressed(O/'rock-y3072-fields-v1.npz',sourceCut=pp,sourceAField=af,sourceBField=bf)
 raw=R/'tiles/r10_c11-candidate.png';tile=Image.open(raw).convert('RGB');tile.paste(Image.fromarray(out),(0,2957));dest=O/'r10_c11-internal-v1.png';tile.save(dest);h.p.derived(dest,[raw,O/'rock-y3072-replacement-v1.png'],{'method':'exact native overlap replacement at [0,2957,2048,230]','formalAccepted':False});qa(tile,'internal-v1',dest)
 h.p.write(O/'internal-v1.json',{'candidate':str(dest),'sha256':h.p.sha(dest),'repairSource':str(O/'rock-y3072-replacement-v1.png'),'origin':[0,2957],'sourceMask':str(O/'rock-y3072-source-choice-v1.png'),'sourceFields':str(O/'rock-y3072-fields-v1.npz'),'maxField':float(max(abs(af).max(),abs(bf).max())),'nativeSources':[str(p) for p in sources],'formalAccepted':False})
if __name__=='__main__':run()

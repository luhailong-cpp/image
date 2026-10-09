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



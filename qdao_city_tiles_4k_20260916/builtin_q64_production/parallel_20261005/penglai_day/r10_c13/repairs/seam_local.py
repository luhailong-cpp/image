from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parent
T=R.parent
sys.path.insert(0,str(T))
import helper as h
def arr(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)
def save(a,p,sources,op):
    Image.fromarray(np.rint(np.clip(a,0,255)).astype('uint8')).save(p)
    h.p.derived(p,sources,op)
def smooth1(a,radius=24):
    a=np.pad(a,((radius,radius),(0,0)),mode='edge');cs=np.pad(np.cumsum(a,axis=0),((1,0),(0,0)))
    return (cs[2*radius+1:]-cs[:-2*radius-1])/(2*radius+1)
def smooth2(a,r=24):
    for axis in [0,1]:
        p=[(0,0)]*3;p[axis]=(r,r);ap=np.pad(a,p,mode='edge')
        p=[(0,0)]*3;p[axis]=(1,0);cs=np.pad(np.cumsum(ap,axis=axis,dtype=np.float64),p)
        sl1=[slice(None)]*3;sl2=[slice(None)]*3;sl1[axis]=slice(2*r+1,None);sl2[axis]=slice(None,-2*r-1)
        a=(cs[tuple(sl1)]-cs[tuple(sl2)])/(2*r+1)
    return a
def seam(a,b,label,margin=55,cap=18,falloff=96,returnends=True):
    # a,b are tangent x normal x RGB; left/upper source is a.
    n,w,_=a.shape
    # Estimate smooth material differences, never blur/resample the actual art.
    difference=a-b
    low=smooth2(difference)
    correction=np.clip(low/2,-cap,cap)
    edge_dist=np.minimum(np.arange(w),np.arange(w)[::-1])
    outer=np.minimum(1,edge_dist/48)[None,:,None]
    fa=-correction*outer;fb=correction*outer
    aa=a+fa;bb=b+fb
    cost=np.mean((aa-bb)**2,axis=2)**.5
    ga=np.diff(a,axis=1,prepend=a[:,:1]);gb=np.diff(b,axis=1,prepend=b[:,:1])
    cost+=np.mean(abs(ga-gb),axis=2)*.6
    cost+=abs(np.arange(w)-w/2)[None,:]*.015
    cost[:,:margin]=1e6;cost[:,w-margin:]=1e6
    if returnends:
        edge=np.minimum(np.arange(n),np.arange(n)[::-1])
        lim=np.minimum(edge*2+2,w//2-margin)
        cost[abs(np.arange(w)[None,:]-w//2)>lim[:,None]]=1e6
    dp=cost[0].copy();back=np.zeros((n,w),dtype=np.int16)
    for i in range(1,n):
        options=np.stack([np.r_[1e9,dp[:-1]],dp,np.r_[dp[1:],1e9]])
        idx=np.argmin(options,axis=0);back[i]=idx-1;dp=cost[i]+options[idx,np.arange(w)]
    path=np.empty(n,dtype=np.int16);path[-1]=np.argmin(dp)
    for i in range(n-1,0,-1):path[i-1]=path[i]+back[i,path[i]]
    dist=np.arange(w)[None,:]-path[:,None]
    own=dist<0
    out=np.where(own[:,:,None],a+fa,b+fb)
    np.savez_compressed(R/(label+'-fields.npz'),path=path,fieldA=fa,fieldB=fb,ownerA=own)
    Image.fromarray(own.astype('uint8')*255).save(R/(label+'-owner-a.png'))
    h.p.write(R/(label+'-method.json'),{'sourceShift':0,'resampling':None,'imageBlur':None,'feather':None,'method':'minimum-error binary native ownership; bounded additive RGB fields along cut','perSourceFieldMax':float(max(abs(fa).max(),abs(fb).max())),'cap':cap,'falloff':falloff,'tangentSmoothingWindow':49,'pathRange':[int(path.min()),int(path.max())]})
    return out
def internal():
    raw=T/'tiles/r10_c13-candidate.png';base=arr(raw);sources=[raw]
    for label,axis,line,seg,left,right in [('roof-x1024','x',1024,0,'p11','p12'),('paving-y3072','y',3072,0,'p31','p41'),('wall-y3072','y',3072,3,'p34','p44')]:
        pa=T/'native'/(left+'.png');pb=T/'native'/(right+'.png');a=arr(pa);b=arr(pb);sources.extend([pa,pb])
        if axis=='x':
            aa=a[115:1139,1024:1254];bb=b[115:1139,0:230]
            out=seam(aa,bb,label);base[seg*1024:(seg+1)*1024,line-115:line+115]=out
        else:
            aa=a[1024:1254,115:1139].transpose(1,0,2);bb=b[0:230,115:1139].transpose(1,0,2)
            out=seam(aa,bb,label).transpose(1,0,2);base[line-115:line+115,seg*1024:(seg+1)*1024]=out
    dest=R/'r10_c13-internal-v2.png';save(base,dest,sources,{'method':'three native-overlap seam repairs; exact fields and ownership alongside','formalAccepted':False});qa(base,'internal-v2',dest)
def qa(a,label,source):
    for axis in ['x','y']:
        for line in [1024,2048,3072]:
            board=np.zeros((1024,1024,3))
            for k in range(4):
                crop=np.rot90(a[k*1024:(k+1)*1024,line-128:line+128]) if axis=='x' else a[line-128:line+128,k*1024:(k+1)*1024]
                board[k*256:(k+1)*256]=crop
            save(board,R/(label+f'-{axis}{line}.png'),[source],{'method':'four native seam crops; vertical strips rotated90; no resampling'})
    board=np.zeros((960,960,3))
    for r,y in enumerate([1024,2048,3072]):
        for c,x in enumerate([1024,2048,3072]):board[r*320:(r+1)*320,c*320:(c+1)*320]=a[y-160:y+160,x-160:x+160]
    save(board,R/(label+'-junctions.png'),[source],{'method':'nine native320px crops, no resampling'})
if __name__=='__main__':internal()

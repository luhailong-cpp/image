import repair_helper as h
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
def cut(cost,x0,x1):
    c=cost[:,x0:x1]; n,w=c.shape;acc=c[0].copy();back=np.zeros((n,w),np.int16)
    for y in range(1,n):
        z=np.stack([np.r_[1e12,acc[:-1]]+.25,acc,np.r_[acc[1:],1e12]+.25]);k=np.argmin(z,axis=0);back[y]=k-1;acc=c[y]+np.min(z,axis=0)
    xs=np.zeros(n,np.int32);xs[-1]=np.argmin(acc)
    for y in range(n-1,0,-1):xs[y-1]=xs[y]+back[y,xs[y]]
    return xs+x0
def gaussian(x,r):return np.asarray(Image.fromarray(x.astype('float32'),'F').filter(ImageFilter.GaussianBlur(r)))
def boxblur(x,r):
    # PIL F mode BoxBlur is unavailable; exact separable moving average field filtering.
    k=2*r+1
    p=np.pad(x,((r,r),(r,r)),mode='edge')
    c=np.pad(np.cumsum(p,axis=0,dtype=np.float64),((1,0),(0,0)));p=(c[k:]-c[:-k])/k
    c=np.pad(np.cumsum(p,axis=1,dtype=np.float64),((0,0),(1,0)));return ((c[:,k:]-c[:,:-k])/k).astype(np.float32)

specs={
 'stripe1024-v1':{'input':'stripe1024-input.png','origin':[397,2842],'cutRanges':[[100,520],[770,1150]]},
 'stripe2048-v1':{'input':'stripe2048-input.png','origin':[1421,2842],'cutRanges':[[80,420],[840,1080]]}
}
for name,s in specs.items():
    src=h.O/s['input'];gen=h.O/(name+'-generated.png');a=np.asarray(Image.open(src).convert('RGB'),dtype=np.float32);b=np.asarray(Image.open(gen).convert('RGB'),dtype=np.float32)
    cost=np.mean(np.minimum(np.abs(a-b),50)**2,axis=2)
    left=cut(cost,*s['cutRanges'][0]);right=cut(cost,*s['cutRanges'][1]);Y,X=np.indices(cost.shape)
    blue=(a[:,:,2]>a[:,:,0]*1.4)&(a[:,:,2]>150)&(a[:,:,0]<180)
    top=np.interp(np.arange(1254),[0,125,250,400,500,627,750,900,1000,1100,1253],[620,577,508,435,379,315,246,171,108,25,0])-20 if name=='stripe1024-v1' else np.interp(np.arange(1254),[0,150,300,500,627,827,1050,1253],[0,90,235,400,500,625,715,740])-12
    m=(X>=left[:,None])&(X<right[:,None])&(Y>=top[None,:])
    if name=='stripe2048-v1':
        bottom=np.where(np.arange(1254)<550,820+.60*np.arange(1254),1437-.47*np.arange(1254))
        m&=Y<bottom[None,:]
    # Difference at the binary ownership perimeter, rejecting contour displacements.
    border=m & (~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1))
    grad=np.max(np.abs(a-np.roll(a,1,0))+np.abs(a-np.roll(a,1,1)),axis=2)
    reliable=border&(grad<35)&(np.max(np.abs(a-b),axis=2)<35)
    weight=boxblur(boxblur(reliable.astype(np.float32),24),24)
    fields=[]
    for ch in range(3):
        num=boxblur(boxblur((a[:,:,ch]-b[:,:,ch])*reliable,24),24)
        f=np.clip(num/np.maximum(weight,1e-6),-12,12)*np.clip(weight*240,0,1)*m
        fields.append(f)
    field=np.stack(fields,axis=2);corrected=np.clip(np.rint(b+field),0,255).astype(np.uint8)
    maskp=h.O/(name+'-mask-v3.png');Image.fromarray((m*255).astype(np.uint8)).save(maskp)
    replacement=h.O/(name+'-replacement-v3.png');Image.fromarray(corrected).save(replacement)
    fieldsP=h.O/(name+'-color-fields-v3.npz');np.savez_compressed(fieldsP,field=field,left=left,right=right)
    out=h.O/(name+'-composite-v3.png');res=np.where(m[:,:,None],corrected,a.astype(np.uint8));Image.fromarray(res).save(out)
    h.derived(maskp,[src,gen],{'method':'minimum color difference binary ownership cuts in stated ranges; canopy-only constraint','cutRanges':s['cutRanges'],'resize':False,'feather':False})
    h.derived(replacement,[gen,src,maskp],{'method':'bounded additive RGB matching at reliable ownership perimeter only','maxAbsoluteColorCorrection':float(np.abs(field).max()),'capPerChannel':12,'fields':str(fieldsP),'fieldSmoothing':'two separable 49px box filters; does not blur image','geometricTransform':None})
    h.derived(out,[src,replacement,maskp],{'method':'binary pixel ownership composite only','originTileXY':s['origin'],'resize':False,'registration':False,'blur':False,'pixelsOutsideMaskUnchanged':True})
    s.update({'replacement':str(replacement),'mask':str(maskp),'composite':str(out),'replacementSha256':h.sha(replacement),'maskSha256':h.sha(maskp),'status':'pending_native_composite_visual_review'})
(h.O/'fabric-merge-manifest-v3.json').write_text(json.dumps({'rawTile':str(h.R/'tiles/r10_c13-candidate.png'),'rawSha256':h.sha(h.R/'tiles/r10_c13-candidate.png'),'repairs':specs},ensure_ascii=False,indent=2),encoding='utf8')

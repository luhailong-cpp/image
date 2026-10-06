from repair import *
import numpy as np
seg=int(sys.argv[1]);limit=6;cut=915
mode=sys.argv[2] if len(sys.argv)>2 else 'dp'
target=R/f's{seg}-target-native.png';source=R/f's{seg}-repair-v1.png'
T=np.array(Image.open(target).convert('RGB')).astype(np.float32);G=np.array(Image.open(source).convert('RGB')).astype(np.float32)
H,W=T.shape[:2]
def match(x0,x1):
    offsets=np.arange(-limit,limit+1);costs=np.zeros((H,len(offsets)),np.float32)
    for k,s in enumerate(offsets):
        rows=np.clip(np.arange(H)+s,0,H-1)
        raw=((T[:,x0:x1]-G[rows,x0:x1])**2).mean(axis=(1,2))
        costs[:,k]=np.convolve(np.pad(raw,(5,5),mode='edge'),np.ones(11)/11,mode='valid')+0.4*s*s
    acc=costs[0].copy();paths=np.zeros_like(costs,dtype=np.int16)
    for y in range(1,H):
        change=np.abs(offsets[:,None]-offsets[None,:]);choices=acc[:,None]+np.where(change<=1,change*28,1e8)
        best=choices.argmin(axis=0);paths[y]=best;acc=choices[best,np.arange(len(offsets))]+costs[y]
    idx=int(acc.argmin());out=np.zeros(H,np.float32)
    for y in range(H-1,-1,-1):out[y]=offsets[idx];idx=paths[y,idx]
    return np.convolve(np.pad(out,(4,4),mode='edge'),np.ones(9)/9,mode='valid').astype(np.float32)
left=match(623,627);right=match(915,923)
if mode=='landmarks' and seg==2:
    left=np.interp(np.arange(H),[0,450,800,980,1139,1253],[-2,-2,-6,-6,0,0]).astype(np.float32)
    right=np.zeros(H,np.float32)
xx=np.arange(W)[None,:];mid=771
wl=np.clip((mid-xx)/(mid-627),0,1);wr=np.clip((xx-mid)/(915-mid),0,1)
flow=left[:,None]*wl+right[:,None]*wr
sy=np.clip(np.arange(H)[:,None]+flow,0,H-1);iy=np.floor(sy).astype(int);fy=sy-iy;GX=np.arange(W)[None,:]
warped=G[iy,GX]*(1-fy[:,:,None])+G[np.minimum(iy+1,H-1),GX]*fy[:,:,None]
def smooth(v,n=11):return np.stack([np.convolve(np.pad(v[:,i],(n//2,n//2),mode='edge'),np.ones(n)/n,mode='valid') for i in range(3)],axis=1)
dl=np.clip(smooth((T[:,624:627]-warped[:,624:627]).mean(axis=1)),-12,12)
dr=np.clip(smooth((T[:,915:918]-warped[:,915:918]).mean(axis=1)),-12,12)
cl=np.clip((699-xx)/72,0,1);cr=np.clip((xx-843)/72,0,1)
color=dl[:,None,:]*cl[:,:,None]+dr[:,None,:]*cr[:,:,None]
corrected=np.clip(warped+color,0,255).round().astype(np.uint8)
mask=np.zeros((H,W),np.uint8);mask[115:1139,627:915]=255
result=T.astype(np.uint8);result[mask>0]=corrected[mask>0]
field=R/f's{seg}-field-register6.npz';np.savez_compressed(field,source_y_displacement=flow.astype(np.float32),rgb_addition=color.astype(np.float32),left_y_profile=left,right_y_profile=right,mask=mask)
registered=R/f's{seg}-registered6.png';Image.fromarray(corrected).save(registered)
derived(registered,[source,target],{'method':'bounded vertical native seam registration and local additive color','field':str(field),'resampling':'bilinear for y only','verticalDisplacementLimit':6,'actualDisplacementRange':[float(flow[115:1139,627:915].min()),float(flow[115:1139,627:915].max())],'horizontalDisplacement':0,'colorAddLimitPerChannel':12})
joined=R/f's{seg}-joined-register6.png';Image.fromarray(result).save(joined)
derived(joined,[registered,target,R/f's{seg}-mask-v1.png'],{'method':'binary right-only native replacement','rectLTRB':[627,115,915,1139],'noFeather':True})
qa=R/f's{seg}-qa-register6.png';Image.fromarray(result).crop((507,115,1035,1139)).save(qa)
derived(qa,[joined],{'method':'native crop','boxLTRB':[507,115,1035,1139]})
strip=R/f's{seg}-strip-register6.png';Image.fromarray(corrected).crop((627,115,915,1139)).save(strip)
derived(strip,[registered],{'method':'native crop','boxLTRB':[627,115,915,1139],'globalRectXYWH':[49152,32768+(seg-1)*1024,288,1024]})
write(R/f's{seg}-registration6.json',{'createdAt':now(),'source':str(source),'target':str(target),'limitPx':6,'actualRange':[float(flow[115:1139,627:915].min()),float(flow[115:1139,627:915].max())],'field':str(field),'fieldSha256':sha(field),'resampling':'bilinear in y','horizontalDisplacement':0,'colorLimit':12,'colorTaperWidth':72,'maskRectLTRB':[627,115,915,1139],'baselineUnchanged':bool(np.array_equal(result[:,:627],T[:,:627])),'farRightUnchanged':bool(np.array_equal(result[:,915:],T[:,915:])),'visualStatus':'pending'})

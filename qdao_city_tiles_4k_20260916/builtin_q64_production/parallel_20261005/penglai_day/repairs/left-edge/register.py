from repair import *
import numpy as np
T=np.array(Image.open(R/'target-native.png').convert('RGB')).astype(np.float32)
G=np.array(Image.open(R/'repair-v1.png').convert('RGB')).astype(np.float32)
H,W=T.shape[:2]
def match(x0,x1,limit=16):
    offsets=np.arange(-limit,limit+1)
    costs=np.zeros((H,len(offsets)),np.float32)
    for k,s in enumerate(offsets):
        row=np.clip(np.arange(H)+s,0,H-1)
        raw=((T[:,x0:x1]-G[row,x0:x1])**2).mean(axis=(1,2))
        costs[:,k]=np.convolve(np.pad(raw,(5,5),mode='edge'),np.ones(11)/11,mode='valid')+0.2*s*s
    acc=costs[0].copy(); paths=np.zeros_like(costs,dtype=np.int16)
    for y in range(1,H):
        change=np.abs(offsets[:,None]-offsets[None,:])
        choices=acc[:,None]+np.where(change<=1,change*22,1e8)
        best=choices.argmin(axis=0)
        paths[y]=best; acc=choices[best,np.arange(len(offsets))]+costs[y]
    idx=int(acc.argmin()); out=np.zeros(H,np.float32)
    for y in range(H-1,-1,-1):out[y]=offsets[idx];idx=paths[y,idx]
    out=np.convolve(np.pad(out,(4,4),mode='edge'),np.ones(9)/9,mode='valid').astype(np.float32)
    return out
left=match(607,627);right=match(830,854)
xx=np.arange(W)[None,:]
wl=np.clip((740-xx)/113,0,1);wr=np.clip((xx-740)/90,0,1)
flow=left[:,None]*wl+right[:,None]*wr
sy=np.clip(np.arange(H)[:,None]+flow,0,H-1);iy=np.floor(sy).astype(int);fy=sy-iy
GX=np.arange(W)[None,:]
warped=G[iy,GX]*(1-fy[:,:,None])+G[np.minimum(iy+1,H-1),GX]*fy[:,:,None]
# Color field is inferred from the held-out unchanged texture strip on each side.
# It does not generate or hide missing geometry. Smooth only the correction field.
dl=(T[:,624:627]-warped[:,624:627]).mean(axis=1)
dr=(T[:,830:833]-warped[:,830:833]).mean(axis=1)
def smooth(v,n=9):return np.stack([np.convolve(np.pad(v[:,i],(n//2,n//2),mode='edge'),np.ones(n)/n,mode='valid') for i in range(3)],axis=1)
dl=np.clip(smooth(dl),-14,14);dr=np.clip(smooth(dr),-14,14)
cl=np.clip((699-xx)/72,0,1);cr=np.clip((xx-782)/48,0,1)
color=dl[:,None,:]*cl[:,:,None]+dr[:,None,:]*cr[:,:,None]
corrected=np.clip(warped+color,0,255).round().astype(np.uint8)
mask=np.zeros((H,W),np.uint8);mask[115:1139,627:830]=255
result=T.astype(np.uint8);result[mask>0]=corrected[mask>0]
Image.fromarray(result).save(R/'joined-v2.png')
Image.fromarray(corrected).save(R/'registered-v1.png')
np.savez_compressed(R/'correction-field-v2.npz',source_y_displacement=flow.astype(np.float32),rgb_addition=color.astype(np.float32),left_y_profile=left,right_y_profile=right,mask=mask)
derived(R/'registered-v1.png',[R/'repair-v1.png',R/'target-native.png'],{'method':'bounded vertical native seam registration and local additive color match','field':str(R/'correction-field-v2.npz'),'resampling':'bilinear for y only','verticalDisplacementLimit':16,'actualDisplacementRange':[float(flow[115:1139,627:830].min()),float(flow[115:1139,627:830].max())],'horizontalDisplacement':0,'colorAddLimitPerChannel':14})
derived(R/'joined-v2.png',[R/'registered-v1.png',R/'target-native.png',R/'mask-v1.png'],{'method':'binary masked replacement only','maskRectLTRB':[627,115,830,1139],'noFeather':True})
Image.fromarray(result).crop((477,115,980,1139)).save(R/'qa-both-edges-v2.png')
derived(R/'qa-both-edges-v2.png',[R/'joined-v2.png'],{'method':'native crop','boxLTRB':[477,115,980,1139],'jointImageX':150,'rightMaskBoundaryImageX':353})
write(R/'registration-v2.json',{'createdAt':now(),'method':'dynamic-programming vertical profile alignment at unchanged left and right anchor strips; linear spatial taper; local bounded additive color','searchLimitPixels':16,'actualDisplacementRangeWithinMask':[float(flow[115:1139,627:830].min()),float(flow[115:1139,627:830].max())],'xDisplacement':0,'resampling':'bilinear in y','leftRegistrationRegionLTRB':[607,0,627,1254],'rightRegistrationRegionLTRB':[830,0,854,1254],'colorCorrectionLimit':14,'fieldFile':str(R/'correction-field-v2.npz'),'fieldSha256':sha(R/'correction-field-v2.npz'),'maskFile':str(R/'mask-v1.png'),'baselinePreserved':bool(np.array_equal(result[:,:627],T[:,:627])),'farRightPreserved':bool(np.array_equal(result[:,830:],T[:,830:])),'status':'requires_visual_review'})

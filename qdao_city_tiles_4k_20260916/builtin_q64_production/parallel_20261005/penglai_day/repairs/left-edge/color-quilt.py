from repair import *
import numpy as np
O=R/'both-side'
src=[R/'repair-v3.png']+[R/f's{i}-repair-v1.png' for i in [2,3,4]]
imgs=[np.array(Image.open(p).convert('RGB')).astype(np.float32) for p in src]
oldfile=BASE;newfile=TASK/'tiles/r09_c13-raw-candidate.png'
old=np.array(Image.open(oldfile).convert('RGB'));new=np.array(Image.open(newfile).convert('RGB'))
base=np.concatenate([old[:,3469:4096],new[:,:627]],axis=1)
paths=np.load(O/'joint-quilt-paths-v2.npz')
def lowpass(a,r=24):
    v=np.pad(a.astype(np.float64),((r,r),(r,r),(0,0)),mode='edge');s=np.pad(v,((1,0),(1,0),(0,0))).cumsum(0).cumsum(1);k=2*r+1
    return ((s[k:,k:]-s[:-k,k:]-s[k:,:-k]+s[:-k,:-k])/(k*k)).astype(np.float32)
gen=np.zeros((4096,1254,3),np.float32);ids=np.zeros((4096,1254),np.uint8);gen[:1139]=imgs[0][115:];ids[:1139]=1
fields={}
for i in range(1,4):
    start=i*1024-115;end=min(start+1254,4096);p=paths[f'y{i*1024}'];current=imgs[i].copy()
    diff=np.clip(lowpass(gen[start:start+230]-current[:230]),-10,10)
    allDelta=np.concatenate([diff,np.repeat(diff[-1:],1024,axis=0)],axis=0)
    yy=np.arange(1254)[:,None];distance=yy-p[None,:]
    weight=np.where(distance>=0,np.clip(1-distance/96,0,1),0)
    field=allDelta*weight[:,:,None];fields[f'top{i}']=field.astype(np.float16);current=np.clip(current+field,0,255)
    mask=(np.arange(end-start)[:,None]>=p[None,:]);g=gen[start:end];g[mask]=current[:end-start][mask];ii=ids[start:end];ii[mask]=i+1
left=paths['left'];right=paths['right'];xx=np.arange(1254)[None,:];mask=(xx>=left[:,None])&(xx<right[:,None])
distance=np.minimum(xx-left[:,None],right[:,None]-1-xx)
weight=np.where(mask,np.clip(1-distance/96,0,1),0)
delta=np.clip(lowpass(base.astype(np.float32)-gen),-10,10);outerField=delta*weight[:,:,None];fields['outer']=outerField.astype(np.float16)
corrected=np.clip(gen+outerField,0,255).round().astype(np.uint8);joined=base.copy();joined[mask]=corrected[mask]
fieldp=O/'joint-quilt-color-fields-v3.npz';np.savez_compressed(fieldp,**fields)
sp=O/'joint-quilt-native-v3.png';Image.fromarray(joined).save(sp)
derived(sp,src+[oldfile,newfile],{'method':'native minimum-error cuts plus bounded low-frequency additive RGB seam match','paths':str(O/'joint-quilt-paths-v2.npz'),'mask':str(O/'joint-quilt-mask-v2.png'),'colorFields':str(fieldp),'colorFieldSha256':sha(fieldp),'colorLimitPerStage':10,'colorTaperPixels':96,'fieldLowpassBox':49,'imageBlur':False,'imageFeather':False,'resampling':None,'displacement':0,'globalRectXYWH':[48525,32768,1254,4096]})
oldcandidate=old.copy();newcandidate=new.copy();oldcandidate[:,3469:4096]=joined[:,:627];newcandidate[:,:627]=joined[:,627:]
cp=O/'c12-right-revised-candidate-v3.png';npth=O/'c13-left-revised-candidate-v3.png';Image.fromarray(oldcandidate).save(cp);Image.fromarray(newcandidate).save(npth)
derived(cp,[oldfile,sp],{'method':'native masked replacement into new derivative','destinationX':3469,'stripCropLTRB':[0,0,627,4096],'originalSourceUnchanged':True})
derived(npth,[newfile,sp],{'method':'native masked replacement into new derivative','destinationX':0,'stripCropLTRB':[627,0,1254,4096]})
for seg in range(4):
    for label,x in [('left-outer',135),('shared',627),('right-outer',1119)]:
        lo=max(0,x-135);hi=min(1254,x+135);box=(lo,seg*1024,hi,(seg+1)*1024);q=O/f'qa-v3-{label}-s{seg+1}.png';Image.fromarray(joined).crop(box).transpose(Image.Transpose.ROTATE_90).save(q);derived(q,[sp],{'method':'native crop and90degree rotation','boxLTRB':box})
for y in [1024,2048,3072]:
    q=O/f'qa-v3-junction-y{y}.png';box=(0,y-160,1254,y+160);Image.fromarray(joined).crop(box).save(q);derived(q,[sp],{'method':'native crop','boxLTRB':box})
write(O/'proposal-v3.json',{'createdAt':now(),'status':'color_matched_native_quilt_candidate_pending_review','newC12':str(cp),'newC12Sha256':sha(cp),'newC13':str(npth),'newC13Sha256':sha(npth),'jointStrip':str(sp),'jointStripSha256':sha(sp),'mask':str(O/'joint-quilt-mask-v2.png'),'provenanceMap':str(O/'joint-quilt-provenance-v2.png'),'pathFile':str(O/'joint-quilt-paths-v2.npz'),'colorFields':str(fieldp),'resampling':None,'displacement':0,'imageBlur':False,'imageFeather':False,'colorLimitPerStage':10,'originalC12File':str(oldfile),'originalC12Sha256':sha(oldfile),'sourceC13RawFile':str(newfile),'sourceC13RawSha256':sha(newfile),'c12Left3509ColumnsUnchanged':bool(np.array_equal(oldcandidate[:,:3509],old[:,:3509])),'c13Beyond587ColumnsUnchanged':bool(np.array_equal(newcandidate[:,587:],new[:,587:])),'formalAccepted':False})

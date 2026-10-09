from helper import *
import numpy as np
# Import only pure helpers before merge script's full-image construction.
ns={};exec((R/'merge_returns.py').read_text(encoding='utf8').split('full=np.concatenate')[0],ns)
path,cost,lowpass=ns['path'],ns['cost'],ns['lowpass']
fp=R/'output/r08_c12-south-candidate-v3.png';north=np.array(Image.open(fp).convert('RGB'));old=north[3000:4096,1500:2754].copy()
src=R/'references/return-trim-input.png';a=np.array(Image.open(src).convert('RGB'));gf=R/'native/return-trim.png';g=np.array(Image.open(gf).convert('RGB'));c=cost(a,g)
left=path(c[:,370:400])+370;right=path(c[:,610:642])+610;top=path(c[157:188].T)+157;bottom=path(c[968:1002].T)+968
Y,X=np.mgrid[:1254,:1254];m=(X>=left[:,None])&(X<right[:,None])&(Y>=top[None,:])&(Y<bottom[None,:]);dist=np.minimum.reduce([X-left[:,None],right[:,None]-1-X,Y-top[None,:],bottom[None,:]-1-Y]);field=np.clip(lowpass(a.astype('float32')-g),-6,6)*np.where(m,np.clip(1-dist/48,0,1),0)[:,:,None];corr=np.clip(np.rint(g+field),0,255).astype('uint8');a[m]=corr[m]
assert not m[1096:].any()
north[3000:,1500:2754]=a[:1096]
dest=R/'output/r08_c12-south-candidate-v4.png';Image.fromarray(north).save(dest);mf=R/'output/return-trim-mask-v4.png';Image.fromarray(m.astype('uint8')*255).save(mf);ff=R/'output/return-trim-fields-v4.npz';np.savez_compressed(ff,field=field.astype('float16'),left=left,right=right,top=top,bottom=bottom)
qa=R/'qa/return-trim-merged-v4.png';Image.fromarray(a).save(qa);p.derived(qa,[fp,gf],{'method':'native panel patch with binary mask and bounded RGB field','combinedOriginXY':[1500,3000],'mask':str(mf),'fields':str(ff),'fieldCap':6,'noResize':True})
base=np.array(Image.open(N).convert('RGB'));diff=np.any(north!=base,axis=2);df=R/'output/r08_c12-south-candidate-v4-exact-diff.png';Image.fromarray(diff.astype('uint8')*255).save(df)
p.derived(dest,[fp,gf],{'method':'native whole panel contour correction from actual AI output','mask':str(mf),'fieldFile':str(ff),'actualDiffFromInternalV2':str(df),'resample':None,'imageBlur':False,'feather':False})
p.derived(df,[dest,N],{'method':'exact binary RGB inequality'})
ys,xs=np.where(diff);p.write(R/'output/trim-integration-v4.json',{'candidate':str(dest),'sha256':p.sha(dest),'base':str(N),'baseSha256':p.sha(N),'exactDiffMask':str(df),'maskSha256':p.sha(df),'bboxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedPixelCount':int(diff.sum()),'localNativePatch':str(gf),'localMask':str(mf),'fields':str(ff),'qa':str(qa),'formalAccepted':False})
print(p.sha(dest))

from returns import *
import numpy as np
from PIL import ImageDraw
def path(cost):
 h,w=cost.shape;ptr=np.zeros((h,w),np.int8);acc=cost[0].copy()
 for y in range(1,h):
  choices=np.stack([np.pad(acc[:-1],(1,0),constant_values=1e12)+.6,acc,np.pad(acc[1:],(0,1),constant_values=1e12)+.6]);k=choices.argmin(0);ptr[y]=k-1;acc=choices[k,np.arange(w)]+cost[y]
 x=int(acc.argmin());v=np.zeros(h,np.int32)
 for y in range(h-1,-1,-1):v[y]=x;x+=int(ptr[y,x])
 return v
def cost(a,b):
 a=a.astype('float32');b=b.astype('float32')
 return np.mean(abs(a-b),2)+1.5*(np.mean(abs(np.diff(a,axis=0,prepend=a[:1])-np.diff(b,axis=0,prepend=b[:1])),2)+np.mean(abs(np.diff(a,axis=1,prepend=a[:,:1])-np.diff(b,axis=1,prepend=b[:,:1])),2))
def lowpass(a,r=24):
 v=np.pad(a.astype(np.float64),((r,r),(r,r),(0,0)),mode='edge');s=np.pad(v,((1,0),(1,0),(0,0))).cumsum(0).cumsum(1);k=2*r+1
 return ((s[k:,k:]-s[:-k,k:]-s[k:,:-k]+s[:-k,:-k])/(k*k)).astype('float32')
full=np.concatenate([np.array(Image.open(A).convert('RGB')),np.array(Image.open(D).convert('RGB'))],axis=0)
records=[]
params={'return-curb':{'left':[40,150],'right':[1180,1249],'top':[275,400],'bottom':[865,1020]},'return-wood':{'left':[25,160],'right':[615,735],'top':[275,400],'bottom':[835,970]}}
for name in ['return-curb','return-wood']:
 x,y,xx,yy=BOXES[name];a=full[y:yy,x:xx].copy();g=np.array(Image.open(R/'native'/f'{name}.png').convert('RGB'));c=cost(a,g);q=params[name]
 left=path(c[:,q['left'][0]:q['left'][1]])+q['left'][0];right=path(c[:,q['right'][0]:q['right'][1]])+q['right'][0]
 top=path(c[q['top'][0]:q['top'][1]].T)+q['top'][0];bottom=path(c[q['bottom'][0]:q['bottom'][1]].T)+q['bottom'][0]
 Y,X=np.mgrid[:1254,:1254];mask=(X>=left[:,None])&(X<right[:,None])&(Y>=top[None,:])&(Y<bottom[None,:]);dist=np.minimum.reduce([X-left[:,None],right[:,None]-1-X,Y-top[None,:],bottom[None,:]-1-Y])
 weight=np.where(mask,np.clip(1-dist/64,0,1),0);field=np.clip(lowpass(a.astype('float32')-g),-10,10)*weight[:,:,None];corr=np.clip(np.rint(g+field),0,255).astype('uint8');a[mask]=corr[mask];full[y:yy,x:xx]=a
 maskfp=R/'output'/f'{name}-mask-v2.png';fieldfp=R/'output'/f'{name}-fields-v2.npz';qa=R/'qa'/f'{name}-merged-v2.png';Image.fromarray(mask.astype('uint8')*255).save(maskfp);np.savez_compressed(fieldfp,field=field.astype('float16'),left=left,right=right,top=top,bottom=bottom);Image.fromarray(a).save(qa)
 p.derived(qa,[A,D,R/'native'/f'{name}.png'],{'method':'same-coordinate binary local repair','sourceBoxLTRBCombined':BOXES[name],'mask':str(maskfp),'field':str(fieldfp),'colorCap':10,'fieldTaper':64,'imageBlur':False,'resample':None})
 records.append({'name':name,'source':str(R/'native'/f'{name}.png'),'sourceSha256':p.sha(R/'native'/f'{name}.png'),'box':BOXES[name],'mask':str(maskfp),'maskSha256':p.sha(maskfp),'fields':str(fieldfp),'fieldSha256':p.sha(fieldfp),'parameters':q})
npth=R/'output/r08_c12-south-candidate-v2.png';spth=R/'output/r09_c12-north-candidate-v2.png';Image.fromarray(full[:4096]).save(npth);Image.fromarray(full[4096:]).save(spth)
for file,base in [(npth,N),(spth,S)]:
 after=np.array(Image.open(file).convert('RGB'));before=np.array(Image.open(base).convert('RGB'));mask=np.any(after!=before,axis=2);mf=R/'output'/(file.stem+'-exact-diff.png');Image.fromarray(mask.astype('uint8')*255).save(mf);p.derived(file,[base,A,D]+[R/'native'/f'{n}.png' for n in params],{'method':'native joint plus two local AI return repairs','sourceOriginalUnchanged':True,'actualDiffMask':str(mf),'repairs':records});p.derived(mf,[file,base],{'method':'exact binary RGB pixel inequality'});ys,xs=np.where(mask);records.append({'candidate':str(file),'sha256':p.sha(file),'base':str(base),'baseSha256':p.sha(base),'exactDiffMask':str(mf),'maskSha256':p.sha(mf),'bboxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'changedPixelCount':int(mask.sum())})
joint=R/'output/joint-quilt-native-v2.png';Image.fromarray(full[3469:4973]).save(joint);p.derived(joint,[npth,spth],{'method':'native combined strip crop','globalRectXYWH':[45056,32141,4096,1504],'sharedLocalY':627,'noResize':True})
p.write(R/'output/proposal-v2.json',{'createdAt':p.stamp(),'status':'pending_native_visual_QA','records':records,'joint':str(joint),'jointSha256':p.sha(joint),'currentFilesOverwritten':False})
print(json.dumps(records[-2:],indent=2))

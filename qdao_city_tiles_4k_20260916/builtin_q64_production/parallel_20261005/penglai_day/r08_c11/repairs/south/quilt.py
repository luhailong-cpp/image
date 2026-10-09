from helper import *
import numpy as np
from PIL import ImageDraw
O=R/'output'
sources=[R/'native'/f's{i}.png' for i in range(1,5)]
imgs=[np.array(Image.open(f).convert('RGB'),np.float32) for f in sources]
base=np.array(Image.open(R/'references/joint-input-native.png').convert('RGB'))
def path(cost):
 h,w=cost.shape;ptr=np.zeros((h,w),np.int8);acc=cost[0].copy()
 for y in range(1,h):
  choices=np.stack([np.pad(acc[:-1],(1,0),constant_values=1e12)+.4,acc,np.pad(acc[1:],(0,1),constant_values=1e12)+.4]);k=choices.argmin(axis=0);ptr[y]=k-1;acc=choices[k,np.arange(w)]+cost[y]
 x=int(acc.argmin());v=np.zeros(h,np.int32)
 for y in range(h-1,-1,-1):v[y]=x;x+=int(ptr[y,x])
 return v
def cost(a,b):
 a=a.astype(np.float32);b=b.astype(np.float32)
 return np.mean(abs(a-b),2)+.8*(np.mean(abs(np.diff(a,axis=0,prepend=a[:1])-np.diff(b,axis=0,prepend=b[:1])),2)+np.mean(abs(np.diff(a,axis=1,prepend=a[:,:1])-np.diff(b,axis=1,prepend=b[:,:1])),2))
def lowpass(a,r=24):
 v=np.pad(a.astype(np.float64),((r,r),(r,r),(0,0)),mode='edge');s=np.pad(v,((1,0),(1,0),(0,0))).cumsum(0).cumsum(1);k=2*r+1
 return ((s[k:,k:]-s[:-k,k:]-s[k:,:-k]+s[:-k,:-k])/(k*k)).astype(np.float32)
gen=np.zeros_like(base,dtype=np.float32);ids=np.zeros(base.shape[:2],np.uint8);gen[:,:1254]=imgs[0];ids[:,:1254]=1
paths={};fields={}
for i in range(1,4):
 start=STARTS[i];overlap=STARTS[i-1]+1254-start;cur=imgs[i].copy();v=path(cost(gen[:,start:start+overlap],cur[:,:overlap])[:,35:overlap-35])+35;paths[f'x{i+1}']=v
 diff=np.clip(lowpass(gen[:,start:start+overlap]-cur[:,:overlap]),-10,10);delta=np.concatenate([diff,np.repeat(diff[:,-1:],1254-overlap,axis=1)],axis=1)
 dist=np.arange(1254)[None,:]-v[:,None];weight=np.where(dist>=0,np.clip(1-dist/96,0,1),0);field=delta*weight[:,:,None];fields[f'left{i+1}']=field.astype(np.float16);cur=np.clip(cur+field,0,255)
 mask=np.arange(1254)[None,:]>=v[:,None];gen[:,start:start+1254][mask]=cur[mask];ids[:,start:start+1254][mask]=i+1
c=cost(base,gen);top=path(c[35:231].T)+35;bottom=path(c[1024:1219].T)+1024;paths['top']=top;paths['bottom']=bottom
yy=np.arange(1254)[:,None];mask=(yy>=top[None,:])&(yy<bottom[None,:]);distance=np.minimum(yy-top[None,:],bottom[None,:]-1-yy);weight=np.where(mask,np.clip(1-distance/96,0,1),0)
delta=np.clip(lowpass(base.astype(np.float32)-gen),-10,10);outerfield=delta*weight[:,:,None];fields['outer']=outerfield.astype(np.float16)
corrected=np.clip(gen+outerfield,0,255).round().astype(np.uint8);joined=base.copy();joined[mask]=corrected[mask]
sp=O/'joint-quilt-native-v1.png';mp=O/'joint-quilt-mask-v1.png';ip=O/'joint-quilt-provenance-v1.png';pp=O/'joint-quilt-paths-v1.npz';fp=O/'joint-quilt-fields-v1.npz'
Image.fromarray(joined).save(sp);Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(np.where(mask,ids*50,0).astype(np.uint8)).save(ip);np.savez_compressed(pp,**paths);np.savez_compressed(fp,**fields)
op={'method':'Native minimum-error binary ownership cuts plus finite additive RGB fields','globalRectXYWH':[40960,32141,4096,1254],'sharedGlobalY':32768,'sourceGlobalOriginsXY':[[40960+x,32141] for x in STARTS],'sourceOrder':list(map(str,sources)),'mask':str(mp),'provenance':str(ip),'paths':str(pp),'pathSha256':p.sha(pp),'fields':str(fp),'fieldSha256':p.sha(fp),'colorLimitPerStage':10,'maximumCombinedBound':20,'colorTaperPixels':96,'fieldLowpassBox':49,'displacement':0,'resampling':None,'imageBlur':False,'feather':0,'formalAccepted':False}
for dest,method in [(sp,'native joint patch'),(mp,'binary ownership 0=keep locked base,255=replace'),(ip,'0=base,50=s1,100=s2,150=s3,200=s4')]:p.derived(dest,sources+[N,S],dict(op,artifact=method))
north=np.array(Image.open(N).convert('RGB'));south=np.array(Image.open(S).convert('RGB'));north[3469:]=joined[:627];south[:627]=joined[627:]
npth=O/'r08_c11-south-candidate-v1.png';spth=O/'r09_c11-north-candidate-v1.png';Image.fromarray(north).save(npth);Image.fromarray(south).save(spth)
p.derived(npth,[N,sp],{'method':'native same-coordinate joint patch','destinationXY':[0,3469],'patchCropLTRB':[0,0,4096,627],'mask':str(mp),'originalSourceUnchanged':True})
p.derived(spth,[S,sp],{'method':'native same-coordinate joint patch','destinationXY':[0,0],'patchCropLTRB':[0,627,4096,1254],'mask':str(mp),'originalSourceUnchanged':True})
for label,y,half in [('north-return',135,135),('shared',627,160),('south-return',1119,135)]:
 sheet=Image.new('RGB',(1024,(2*half+24)*4),(24,24,24));d=ImageDraw.Draw(sheet)
 for i in range(4):
  box=(i*1024,y-half,(i+1)*1024,y+half);d.text((8,i*(2*half+24)+4),f'{label} segment{i+1} native',fill='white');sheet.paste(Image.fromarray(joined).crop(box),(0,i*(2*half+24)+24))
 q=R/'qa'/f'{label}-full-v1.png';sheet.save(q);p.derived(q,[sp],{'method':'native strips stacked; no resize','centerY':y,'halfHeight':half})
for i in range(1,4):
 x=STARTS[i]+150;box=(x-180,0,x+180,1254);q=R/'qa'/f'junction-s{i+1}-v1.png';Image.fromarray(joined).crop(box).save(q);p.derived(q,[sp],{'method':'native crop','boxLTRB':box})
sheet=Image.new('RGB',(480,1254));sheet.paste(Image.fromarray(joined).crop((0,0,240,1254)),(0,0));sheet.paste(Image.fromarray(joined).crop((3856,0,4096,1254)),(240,0));sheet.save(R/'qa/endpoints-v1.png')
p.write(O/'proposal-v1.json',dict(op,status='pending actual native visual review',northCandidate=str(npth),northSha256=p.sha(npth),southCandidate=str(spth),southSha256=p.sha(spth),jointStrip=str(sp),jointSha256=p.sha(sp),maskSha256=p.sha(mp),cutRanges={'top':[int(top.min()),int(top.max())],'bottom':[int(bottom.min()),int(bottom.max())]},southUnchangedBelowY627=bool(np.array_equal(south[627:],np.array(Image.open(S).convert('RGB'))[627:]))))
print(p.sha(sp),p.sha(npth),p.sha(spth))

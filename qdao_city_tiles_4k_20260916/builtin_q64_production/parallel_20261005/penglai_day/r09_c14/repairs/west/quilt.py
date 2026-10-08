from helper import *
import numpy as np
O=R/'output';O.mkdir(exist_ok=True)
sources=[R/'native'/f'{n}.png' for n in ['s1','s2-v2','s3','s4']]
imgs=[np.array(Image.open(f).convert('RGB')).astype(np.float32) for f in sources]
west=np.array(Image.open(W).convert('RGB'));east=np.array(Image.open(E).convert('RGB'))
base=np.concatenate([west[:,3469:4096],east[:,:627]],axis=1)
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
gen=np.zeros((4096,1254,3),np.float32);ids=np.zeros((4096,1254),np.uint8);gen[:1139]=imgs[0][115:];ids[:1139]=1
paths={};fields={}
for i in range(1,4):
    start=i*1024-115;end=min(start+1254,4096);cur=imgs[i].copy();v=path(cost(gen[start:start+230],cur[:230])[35:195].T)+35;paths[f'y{i*1024}']=v
    diff=np.clip(lowpass(gen[start:start+230]-cur[:230]),-10,10);delta=np.concatenate([diff,np.repeat(diff[-1:],1024,axis=0)],axis=0)
    distance=np.arange(1254)[:,None]-v[None,:];weight=np.where(distance>=0,np.clip(1-distance/96,0,1),0);field=delta*weight[:,:,None];fields[f'top{i}']=field.astype(np.float16);cur=np.clip(cur+field,0,255)
    mask=np.arange(end-start)[:,None]>=v[None,:];gen[start:end][mask]=cur[:end-start][mask];ids[start:end][mask]=i+1
c=cost(base,gen);left=path(c[:,40:231])+40;right=path(c[:,1024:1215])+1024;paths['left']=left;paths['right']=right
xx=np.arange(1254)[None,:];mask=(xx>=left[:,None])&(xx<right[:,None]);distance=np.minimum(xx-left[:,None],right[:,None]-1-xx);weight=np.where(mask,np.clip(1-distance/96,0,1),0)
delta=np.clip(lowpass(base.astype(np.float32)-gen),-10,10);outerfield=delta*weight[:,:,None];fields['outer']=outerfield.astype(np.float16)
corrected=np.clip(gen+outerfield,0,255).round().astype(np.uint8);joined=base.copy();joined[mask]=corrected[mask]
sp=O/'joint-quilt-native-v1.png';mp=O/'joint-quilt-mask-v1.png';ip=O/'joint-quilt-provenance-v1.png';pp=O/'joint-quilt-paths-v1.npz';fp=O/'joint-quilt-fields-v1.npz'
Image.fromarray(joined).save(sp);Image.fromarray(mask.astype(np.uint8)*255).save(mp);Image.fromarray(np.where(mask,ids*50,0).astype(np.uint8)).save(ip);np.savez_compressed(pp,**paths);np.savez_compressed(fp,**fields)
op={'method':'Native minimum-error binary ownership cuts plus finite additive RGB correction fields','globalRectXYWH':[52621,32768,1254,4096],'sharedGlobalX':53248,'sourceGlobalOriginsXY':[[52621,32653+i*1024] for i in range(4)],'sourceOrder':list(map(str,sources)),'mask':str(mp),'provenance':str(ip),'pathFile':str(pp),'pathSha256':p.sha(pp),'colorFields':str(fp),'fieldSha256':p.sha(fp),'colorLimitPerStage':10,'maximumCombinedBound':20,'colorTaperPixels':96,'fieldLowpassBox':49,'displacement':0,'resampling':None,'imageBlur':False,'feather':0,'formalAccepted':False}
for dest,method in [(sp,'native joint patch'),(mp,'binary ownership mask 0=keep locked base 255=replace by joint patch'),(ip,'provenance0=base,50=s1,100=s2-v2,150=s3,200=s4')]:p.derived(dest,sources+[W,E],dict(op,artifact=method))
wc=west.copy();ec=east.copy();wc[:,3469:]=joined[:,:627];ec[:,:627]=joined[:,627:]
wp=O/'r09_c13-right-candidate-v1.png';ep=O/'r09_c14-left-candidate-v1.png';Image.fromarray(wc).save(wp);Image.fromarray(ec).save(ep)
p.derived(wp,[W,sp],{'method':'masked native joint patch applied into new derivative','destinationXY':[3469,0],'patchCropLTRB':[0,0,627,4096],'mask':str(mp),'resampling':None})
p.derived(ep,[E,sp],{'method':'masked native joint patch applied into new derivative','destinationXY':[0,0],'patchCropLTRB':[627,0,1254,4096],'mask':str(mp),'resampling':None,'integrationWarning':'East base raw; integrate mask onto internally repaired candidate instead of overwriting whole candidate'})
for label,x in [('left-return',135),('shared',627),('right-return',1119)]:
    sheet=Image.new('RGB',(1024,1176),(24,24,24));from PIL import ImageDraw;d=ImageDraw.Draw(sheet)
    for i in range(4):
        box=(x-135,i*1024,x+135,(i+1)*1024);d.text((8,i*294+4),f'{label} s{i+1}: native pixels rotated90',fill='white');sheet.paste(Image.fromarray(joined).crop(box).transpose(Image.Transpose.ROTATE_90),(0,i*294+24))
    q=R/'qa'/f'{label}-full-v1.png';sheet.save(q);p.derived(q,[sp],{'method':'integer270pxwide strips rotated90,stacked4','centerX':x,'resize':False})
for y in [1024,2048,3072]:
    q=R/'qa'/f'junction-y{y}-v1.png';box=(0,y-160,1254,y+160);Image.fromarray(joined).crop(box).save(q);p.derived(q,[sp],{'method':'native integer crop','boxLTRB':box,'resize':False})
sheet=Image.new('RGB',(1254,480));sheet.paste(Image.fromarray(joined).crop((0,0,1254,240)),(0,0));sheet.paste(Image.fromarray(joined).crop((0,3856,1254,4096)),(0,240));q=R/'qa/endpoints-v1.png';sheet.save(q);p.derived(q,[sp],{'method':'native top240 and bottom240 stacked','resize':False})
report=dict(op,status='pending_native_visual_review',jointStrip=str(sp),jointStripSha256=p.sha(sp),westCandidate=str(wp),westCandidateSha256=p.sha(wp),eastCandidate=str(ep),eastCandidateSha256=p.sha(ep),westUnchangedBeforeX3509=bool(np.array_equal(wc[:,:3509],west[:,:3509])),eastUnchangedBeyondX587=bool(np.array_equal(ec[:,587:],east[:,587:])),cutRanges={'left':[int(left.min()),int(left.max())],'right':[int(right.min()),int(right.max())]},topRowsChanged={'west':int(np.count_nonzero(np.any(wc[0]!=west[0],axis=1))),'east':int(np.count_nonzero(np.any(ec[0]!=east[0],axis=1)))},bottomRowsChanged={'west':int(np.count_nonzero(np.any(wc[-1]!=west[-1],axis=1))),'east':int(np.count_nonzero(np.any(ec[-1]!=east[-1],axis=1)))},cornersRequireJointQA=True)
p.write(O/'proposal-v1.json',report);print(json.dumps({k:report[k] for k in ['jointStrip','cutRanges','topRowsChanged','bottomRowsChanged']}))

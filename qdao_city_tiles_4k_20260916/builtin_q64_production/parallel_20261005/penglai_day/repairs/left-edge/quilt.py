from repair import *
import numpy as np
O=R/'both-side';O.mkdir(exist_ok=True)
src=[R/'repair-v3.png']+[R/f's{i}-repair-v1.png' for i in [2,3,4]]
imgs=[np.array(Image.open(p).convert('RGB')) for p in src]
oldfile=BASE;newfile=TASK/'tiles/r09_c13-raw-candidate.png'
old=np.array(Image.open(oldfile).convert('RGB'));new=np.array(Image.open(newfile).convert('RGB'))
base=np.concatenate([old[:,3469:4096],new[:,:627]],axis=1)
def path(cost):
    # Minimum error path; neighbors differ by <=1pixel. No image interpolation.
    h,w=cost.shape;ptr=np.zeros((h,w),np.int8);acc=cost[0].copy()
    for y in range(1,h):
        choices=np.stack([np.pad(acc[:-1],(1,0),constant_values=1e12)+0.4,acc,np.pad(acc[1:],(0,1),constant_values=1e12)+0.4])
        k=choices.argmin(axis=0);ptr[y]=k-1;acc=choices[k,np.arange(w)]+cost[y]
    x=int(acc.argmin());p=np.zeros(h,np.int32)
    for y in range(h-1,-1,-1):p[y]=x;x+=int(ptr[y,x])
    return p
def cost(a,b):
    aa=a.astype(np.float32);bb=b.astype(np.float32)
    # Color mismatch and mismatch of first derivatives, without pixel smoothing.
    d=np.mean(np.abs(aa-bb),axis=2)
    gy=np.mean(np.abs(np.diff(aa,axis=0,prepend=aa[:1])-np.diff(bb,axis=0,prepend=bb[:1])),axis=2)
    gx=np.mean(np.abs(np.diff(aa,axis=1,prepend=aa[:,:1])-np.diff(bb,axis=1,prepend=bb[:,:1])),axis=2)
    return d+0.8*(gx+gy)
gen=np.zeros((4096,1254,3),np.uint8);ids=np.zeros((4096,1254),np.uint8)
gen[:1139]=imgs[0][115:];ids[:1139]=1
paths={}
for i in range(1,4):
    start=i*1024-115;end=min(start+1254,4096)
    overlap=230
    c=cost(gen[start:start+overlap],imgs[i][:overlap])
    # Search within overlapping native context, shared by both source images.
    p=path(c[35:195].T)+35;paths[f'y{i*1024}']=p
    yy=np.arange(end-start)[:,None];mask=yy>=p[None,:]
    g=gen[start:end];g[mask]=imgs[i][:end-start][mask]
    ii=ids[start:end];ii[mask]=i+1
# Global vertical cuts avoid per-segment discontinuities at repair outer edge.
c=cost(base,gen)
left=path(c[:,40:231])+40;right=path(c[:,1024:1215])+1024
xx=np.arange(1254)[None,:];mask=(xx>=left[:,None])&(xx<right[:,None]);joined=base.copy();joined[mask]=gen[mask]
oldcandidate=old.copy();newcandidate=new.copy();oldcandidate[:,3469:4096]=joined[:,:627];newcandidate[:,:627]=joined[:,627:]
sp=O/'joint-quilt-native-v2.png';Image.fromarray(joined).save(sp)
mp=O/'joint-quilt-mask-v2.png';Image.fromarray(mask.astype(np.uint8)*255).save(mp)
ip=O/'joint-quilt-provenance-v2.png';Image.fromarray(np.where(mask,ids*50,0).astype(np.uint8)).save(ip)
paths.update({'left':left,'right':right});pp=O/'joint-quilt-paths-v2.npz';np.savez_compressed(pp,**paths)
derived(mp,src+[oldfile,newfile],{'method':'native minimum-error overlap cuts; binary mask','pathFile':str(pp),'resampling':None,'feather':0})
derived(ip,src+[oldfile,newfile],{'method':'source provenance;0=base,50=s1,100=s2,150=s3,200=s4','resampling':None})
derived(sp,src+[oldfile,newfile],{'method':'native minimum-error seam cuts, no warp or feather','globalRectXYWH':[48525,32768,1254,4096],'mask':str(mp),'provenance':str(ip),'paths':str(pp),'pathSha256':sha(pp),'sourceGlobalOriginY':[32653,33677,34701,35725],'displacement':0,'resampling':None,'colorCorrection':None})
cp=O/'c12-right-revised-candidate-v2.png';npth=O/'c13-left-revised-candidate-v2.png';Image.fromarray(oldcandidate).save(cp);Image.fromarray(newcandidate).save(npth)
derived(cp,[oldfile,sp],{'method':'native replacement in new derivative only','copyStripLeft627toOriginalX3469':True,'mask':str(mp),'resampling':None})
derived(npth,[newfile,sp],{'method':'native replacement in new derivative only','copyStripRight627toOriginalX0':True,'mask':str(mp),'resampling':None})
for seg in range(4):
    for label,x in [('left-outer',135),('shared',627),('right-outer',1119)]:
        lo=max(0,x-135);hi=min(1254,x+135);box=(lo,seg*1024,hi,(seg+1)*1024)
        q=O/f'qa-v2-{label}-s{seg+1}.png';Image.fromarray(joined).crop(box).transpose(Image.Transpose.ROTATE_90).save(q);derived(q,[sp],{'method':'native crop and90degree rotation','boxLTRB':box})
for y in [1024,2048,3072]:
    q=O/f'qa-v2-junction-y{y}.png';box=(0,y-160,1254,y+160);Image.fromarray(joined).crop(box).save(q);derived(q,[sp],{'method':'native crop','boxLTRB':box})
write(O/'proposal-v2.json',{'createdAt':now(),'status':'native_quilt_candidate_pending_visual_review','originalC12':str(oldfile),'originalC12Sha256':sha(oldfile),'newC12':str(cp),'newC12Sha256':sha(cp),'newC13':str(npth),'newC13Sha256':sha(npth),'jointStrip':str(sp),'mask':str(mp),'provenanceMap':str(ip),'pathFile':str(pp),'leftCutRange':[int(left.min()),int(left.max())],'rightCutRange':[int(right.min()),int(right.max())],'sourceOffsets':{'x':48525,'ys':[32653,33677,34701,35725]},'noResampling':True,'noColorCorrection':True,'noFeather':True,'originalC12MatchesHandoff':sha(oldfile)==H['baselineCandidates'][-1]['sha256'],'c12Left3509ColumnsUnchanged':bool(np.array_equal(oldcandidate[:,:3509],old[:,:3509])),'c13Beyond587ColumnsUnchanged':bool(np.array_equal(newcandidate[:,587:],new[:,587:])),'formalAccepted':False})

from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T));import internal_qa as q
from merge_shared import save
from finalize_shared_v4 import recordpatch
h=q.h
inp=R/'shared-output-v5';out=R/'shared-output-v6';out.mkdir(exist_ok=True)
keys=['r09_c11','r09_c12','r10_c11','r10_c12'];a={k:q.arr(inp/f'{k}-candidate.png') for k in keys};old=np.concatenate([a['r10_c11'][1700:2954,3072:],a['r10_c12'][1700:2954,:230]],axis=1)
src=R/'east-joint/native/s3-right-return.png';new=q.arr(src);cost=np.mean(abs(old-new),axis=2);yy,xx=np.mgrid[:1254,:1254]
top=q.path(cost[100:200].T)+100;bottom=q.path(cost[1050:1180].T)+1050;left=q.path(cost[:,250:400])+250;right=q.path(cost[:,900:1010])+900;mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None])
rep,rec=recordpatch(R/'east-joint/output-v6',src,old,new,mask,{'top':top,'bottom':bottom,'left':left,'right':right},[44032,38564],'leaf-water-right-return',[inp/'r10_c11-candidate.png',inp/'r10_c12-candidate.png'])
part=old.copy();part[mask]=rep[mask];a['r10_c11'][1700:2954,3072:]=part[:,:1024];assert not mask[:,1024:].any()
# Real source-color discontinuity on a continuous cliff at y2048: bounded paired RGB-only field.
v=a['r10_c11'];x0,x1,y0,y1=1350,2500,1848,2248;old=v[y0:y1,x0:x1].copy()
jump=np.median(v[2048:2051,x0:x1],axis=0)-np.median(v[2045:2048,x0:x1],axis=0)
j=q.smooth2(jump[None,:,:],24)[0];j=np.clip(j/2,-12,12)
ys=np.arange(y0,y1);xs=np.arange(x1-x0);wY=np.clip(1-abs(ys-2047.5)/200,0,1)**2;wX=np.minimum(np.clip(xs/80,0,1),np.clip((x1-x0-1-xs)/80,0,1));sign=np.where(ys<2048,1,-1)
field=j[None,:,:]*(sign*wY)[:,None,None]*wX[None,:,None]
v[y0:y1,x0:x1]+=field
d=R/'east-joint/output-v6';rp=d/'cliff-colour-replacement.png';mp=d/'cliff-colour-mask.png';fp=d/'cliff-colour-field.npz'
save(v[y0:y1,x0:x1],rp,[inp/'r10_c11-candidate.png'],{'method':'paired bounded12 RGB field on original cliff pixels; no resampling/warp/blur/feather','imageOriginTileXY':[x0,y0]});cm=np.any(abs(field)>0,axis=2);Image.fromarray(cm.astype('uint8')*255).save(mp);np.savez_compressed(fp,field=field,measuredJump=jump,halfJump=j);h.p.derived(mp,[rp],{'method':'nonzero RGB-field ownership mask'})
rec2={'name':'cliffColour','source':str(inp/'r10_c11-candidate.png'),'replacement':str(rp),'mask':str(mp),'fields':str(fp),'globalOriginXY':[40960+x0,36864+y0]}
for k in keys:save(a[k],out/f'{k}-candidate.png',[inp/f'{k}-candidate.png',Path(rec['replacement']),rp],{'method':'exact native ownership and RGB-only correction','formalAccepted':False})
h.p.write(out/'record.json',{'inputStage':str(inp),'repairs':[rec,rec2],'formalAccepted':False})
tile=Image.open(out/'r10_c11-candidate.png');tile.crop((3072,1700,4096,2954)).save(out/'right-return-review.png');tile.crop((1450,1800,2704,2400)).save(out/'cliff-colour-review.png')
b=Image.new('RGB',(1024,1024))
for box,pos in zip([(3250,2100,3762,2612),(3584,2100,4096,2612),(3420,1600,3932,2112),(3420,2600,3932,3112)],[(0,0),(512,0),(0,512),(512,512)]):b.paste(tile.crop(box),pos)
b.save(out/'right-return-edges.png')
north=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0);east=np.concatenate([a['r10_c11'][:,-627:],a['r10_c12'][:,:627]],axis=1)
for axis,v in [('north',north),('east',east)]:
 for i,x in enumerate([0,1024,2048,2842],1):save(v[:,x:x+1254] if axis=='north' else v[x:x+1254],out/f'{axis}-s{i}-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 shared-edge and return review'})
q.qa(tile,'shared-v6',out/'r10_c11-candidate.png')
print(str(out))

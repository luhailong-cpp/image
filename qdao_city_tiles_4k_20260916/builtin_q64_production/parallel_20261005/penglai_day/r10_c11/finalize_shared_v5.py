from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T));import internal_qa as q
from merge_shared import save
from finalize_shared_v4 import recordpatch
h=q.h
inp=R/'shared-output-v4';out=R/'shared-output-v5';out.mkdir(exist_ok=True)
src=R/'east-joint/native/s3-water-return.png';old=q.arr(inp/'r10_c11-candidate.png')[1800:3054,2445:3699];new=q.arr(src);cost=np.mean(abs(old-new),axis=2);yy,xx=np.mgrid[:1254,:1254]
top=q.path(cost[60:160].T)+60;bottom=q.path(cost[990:1150].T)+990;mask=(yy>=top[None,:])&(yy<bottom[None,:])
rep,rec=recordpatch(R/'east-joint/output-v5',src,old,new,mask,{'top':top,'bottom':bottom},[43405,38664],'water-T-return',[inp/'r10_c11-candidate.png'])
keys=['r09_c11','r09_c12','r10_c11','r10_c12'];a={k:q.arr(inp/f'{k}-candidate.png') for k in keys}
a['r10_c11'][1800:3054,2445:3699][mask]=rep[mask]
for k in keys:save(a[k],out/f'{k}-candidate.png',[inp/f'{k}-candidate.png',Path(rec['replacement'])],{'method':'exact native ownership repair','formalAccepted':False})
h.p.write(out/'record.json',{'inputStage':str(inp),'repairs':[rec],'formalAccepted':False})
tile=Image.open(out/'r10_c11-candidate.png')
tile.crop((2445,1800,3699,3054)).save(out/'water-return-review.png')
b=Image.new('RGB',(1024,1024))
for box,pos in zip([(2189,1800,2701,2312),(3443,1800,3955,2312),(2816,1650,3328,2162),(2816,2660,3328,3172)],[(0,0),(512,0),(0,512),(512,512)]):b.paste(tile.crop(box),pos)
b.save(out/'water-return-edges.png')
north=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0);east=np.concatenate([a['r10_c11'][:,-627:],a['r10_c12'][:,:627]],axis=1)
for axis,v in [('north',north),('east',east)]:
 for i,x in enumerate([0,1024,2048,2842],1):save(v[:,x:x+1254] if axis=='north' else v[x:x+1254],out/f'{axis}-s{i}-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 shared-edge and return review'})
q.qa(tile,'shared-v5',out/'r10_c11-candidate.png')
print(str(out))

from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T));import internal_qa as q
from merge_shared import save
from finalize_shared_v4 import recordpatch
h=q.h
inp=R/'shared-output-v6';out=R/'shared-output-v7';out.mkdir(exist_ok=True)
keys=['r09_c11','r09_c12','r10_c11','r10_c12'];a={k:q.arr(inp/f'{k}-candidate.png') for k in keys};old=a['r10_c11'][1773:3027,1421:2675].copy()
src=R/'east-joint/native/s3-cliff-return.png';new=q.arr(src);cost=np.mean(abs(old-new),axis=2);yy,xx=np.mgrid[:1254,:1254]
top=q.path(cost[30:150].T)+30;bottom=q.path(cost[1080:1180].T)+1080;left=q.path(cost[:,50:180])+50;right=q.path(cost[:,1100:1210])+1100;mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None])
rep,rec=recordpatch(R/'east-joint/output-v7',src,old,new,mask,{'top':top,'bottom':bottom,'left':left,'right':right},[42381,38637],'cliff-L-return',[inp/'r10_c11-candidate.png'])
a['r10_c11'][1773:3027,1421:2675][mask]=rep[mask]
for k in keys:save(a[k],out/f'{k}-candidate.png',[inp/f'{k}-candidate.png',Path(rec['replacement'])],{'method':'exact native ownership repair','formalAccepted':False})
h.p.write(out/'record.json',{'inputStage':str(inp),'repairs':[rec],'formalAccepted':False})
tile=Image.open(out/'r10_c11-candidate.png');tile.crop((1421,1773,2675,3027)).save(out/'cliff-return-review.png')
b=Image.new('RGB',(1024,1024))
for box,pos in zip([(1250,1870,1762,2382),(2280,1870,2792,2382),(1800,1640,2312,2152),(1800,2720,2312,3232)],[(0,0),(512,0),(0,512),(512,512)]):b.paste(tile.crop(box),pos)
b.save(out/'cliff-return-edges.png')
q.qa(tile,'shared-v7',out/'r10_c11-candidate.png')
# Final native shared-edge boards and endpoint contexts.
north=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0);east=np.concatenate([a['r10_c11'][:,-627:],a['r10_c12'][:,:627]],axis=1)
for axis,v in [('north',north),('east',east)]:
 for i,x in enumerate([0,1024,2048,2842],1):save(v[:,x:x+1254] if axis=='north' else v[x:x+1254],out/f'{axis}-s{i}-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 shared-edge and return review'})
corner=np.concatenate([np.concatenate([a['r09_c11'][-627:,-627:],a['r09_c12'][-627:,:627]],axis=1),np.concatenate([a['r10_c11'][:627,-627:],a['r10_c12'][:627,:627]],axis=1)],axis=0)
save(corner,out/'corner-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 fourtile-corner QA'})
print(str(out))

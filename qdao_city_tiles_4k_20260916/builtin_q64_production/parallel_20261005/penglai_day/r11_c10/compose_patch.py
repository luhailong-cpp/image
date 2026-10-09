from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import internal_qa as q
h=q.h;R=T/'repairs';starts=[0,1024,2048,2842]
def save(a,p,sources,op):
 Image.fromarray(np.clip(np.rint(a),0,255).astype('uint8')).save(p);h.p.derived(p,sources,op)
def patch(old,new,bands):
 yy,xx=np.mgrid[:1254,:1254];err=np.mean(abs(old-new),2)
 gx=np.diff(old-new,axis=1,prepend=(old-new)[:,:1]);gy=np.diff(old-new,axis=0,prepend=(old-new)[:1]);cost=err+1.5*np.mean(abs(gx)+abs(gy),2)
 def cut(b,axis):
  if isinstance(b,int):return np.full(1254,b,np.int16)
  return q.path(cost[b[0]:b[1]].T)+b[0] if axis=='y' else q.path(cost[:,b[0]:b[1]])+b[0]
 top,bottom,left,right=[cut(b,a) for b,a in zip(bands,['y','y','x','x'])]
 mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None])
 dist=np.minimum.reduce([yy-top[None,:],bottom[None,:]-yy,xx-left[:,None],right[:,None]-xx]);w=np.clip(1-dist/96,0,1)**2*mask
 field=np.clip(q.smooth2(old-new,10),-12,12)*w[:,:,None];rep=np.clip(np.rint(new+field),0,255);out=old.copy();out[mask]=rep[mask]
 return out,rep,mask,field,{'top':top,'bottom':bottom,'left':left,'right':right}
def record(folder,name,old,new,source,origin,bands,transpose=False):
 out,rep,mask,field,cuts=patch(old,new,bands)
 if transpose:rep=rep.transpose(1,0,2);mask=mask.T;field=field.transpose(1,0,2)
 folder.mkdir(parents=True,exist_ok=True);rp=folder/(name+'-replacement.png');mp=folder/(name+'-mask.png');fp=folder/(name+'-fields.npz')
 save(rep,rp,[source],{'method':'nativeAI source with bounded12RGB return field only','fields':str(fp),'zeroWarpResizeBlurFeather':True});Image.fromarray(mask.astype('uint8')*255).save(mp);np.savez_compressed(fp,field=field,**cuts)
 e={'source':str(source),'sourceSha256':h.p.sha(source),'replacement':str(rp),'mask':str(mp),'fields':str(fp),'origin':origin,'maxField':float(abs(field).max())};return out,e

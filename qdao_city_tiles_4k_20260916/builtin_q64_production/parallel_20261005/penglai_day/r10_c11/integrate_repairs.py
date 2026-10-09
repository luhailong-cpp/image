from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import internal_qa as q
h=q.h;R=T/'repairs'
def run():
 raw=T/'tiles/r10_c11-candidate.png';a=q.arr(raw);records=[];yy,xx=np.mgrid[:1254,:1254]
 for name,x in [('cliff-left',0),('cliff-center',1024)]:
  src=R/'native'/f'{name}.png';new=q.arr(src);context=a[2445:3699,x:x+1254].copy();cost=np.mean(abs(context-new),axis=2)
  top=q.path(cost[280:420].T)+280;bottom=q.path(cost[910:1060].T)+910;right=q.path(cost[:,1120:1230])+1120;left=np.zeros(1254,np.int16) if x==0 else q.path(cost[:,20:140])+20
  mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx<right[:,None])&(xx>=left[:,None]);dist=np.minimum(yy-top[None,:],bottom[None,:]-yy);dist=np.minimum(dist,right[:,None]-xx)
  if x:dist=np.minimum(dist,xx-left[:,None])
  w=np.clip(1-dist/96,0,1)**2*mask;field=np.clip(q.smooth2(context-new,12),-10,10)*w[:,:,None];replacement=np.clip(np.rint(new+field),0,255).astype('uint8')
  rp=R/f'{name}-replacement-v2.png';mp=R/f'{name}-mask-v2.png';Image.fromarray(replacement).save(rp);Image.fromarray(mask.astype('uint8')*255).save(mp);fp=R/f'{name}-fields-v2.npz';np.savez_compressed(fp,top=top,bottom=bottom,left=left,right=right,field=field)
  for p in [rp,mp]:h.p.derived(p,[src,raw],{'method':'binary native AI source ownership with bounded10 RGB perimeter field','fieldFile':str(fp),'noResampling':True,'imageBlur':False,'imageFeather':False,'origin':[x,2445]})
  a[2445:3699,x:x+1254][mask]=replacement[mask];records.append({'source':str(src),'replacement':str(rp),'mask':str(mp),'origin':[x,2445],'fields':str(fp),'maxField':float(abs(field).max())})
 dest=R/'r10_c11-internal-v2.png';Image.fromarray(a.astype('uint8')).save(dest);h.p.derived(dest,[raw]+[Path(i[k]) for i in records for k in ['replacement','mask']],{'method':'precise masks insert native AI repairs','formalAccepted':False});q.qa(Image.open(dest),'internal-v2',dest);h.p.write(R/'internal-v2.json',{'candidate':str(dest),'sha256':h.p.sha(dest),'repairs':records,'formalAccepted':False})
 for x in [0,1024]:
  p=R/f'cliff-return-{x}-v2.png';Image.fromarray(a[2445:3699,x:x+1254].astype('uint8')).save(p);h.p.derived(p,[dest],{'method':'native1254 return inspection'})
if __name__=='__main__':run()

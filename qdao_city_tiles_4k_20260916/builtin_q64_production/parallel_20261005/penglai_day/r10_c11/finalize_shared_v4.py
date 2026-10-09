from pathlib import Path
import sys,numpy as np
from PIL import Image,ImageFilter
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T))
import internal_qa as q
from merge_shared import save
from finalize_shared import patch
h=q.h
def returnfield(old,new,mask,width=96):
 yy,xx=np.mgrid[:1254,:1254]
 w=np.clip((1-np.asarray(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.GaussianBlur(32)),dtype=np.float32)/255)*2,0,1)
 edge=np.minimum.reduce([xx,1253-xx,yy,1253-yy])
 w=np.maximum(w,np.clip(1-edge/width,0,1)**2)*mask
 field=np.clip(q.smooth2(old-new,12),-12,12)*w[:,:,None]
 return new+field,field,w
def recordpatch(d,src,old,new,mask,fields,origin,name,refs):
 d.mkdir(exist_ok=True);rep,field,w=returnfield(old,new,mask);fields['field']=field;fields['fieldWeight']=w
 rp=d/(name+'-replacement.png');mp=d/(name+'-mask.png');fp=d/(name+'-fields.npz')
 save(rep,rp,[src]+refs,{'method':'native AI source plus binary minimum-error ownership and bounded12 RGB field; field smoothing only, no image blur','resampling':False,'geometricShift':0})
 Image.fromarray(mask.astype('uint8')*255).save(mp);np.savez_compressed(fp,**fields);h.p.derived(mp,[rp],{'method':'binary ownership mask'})
 return rep,{'name':name,'source':str(src),'replacement':str(rp),'mask':str(mp),'fields':str(fp),'globalOriginXY':origin}
def run():
 inp=R/'shared-output-v3';out=R/'shared-output-v4';out.mkdir(exist_ok=True);keys=['r09_c11','r09_c12','r10_c11','r10_c12'];a={k:q.arr(inp/f'{k}-candidate.png') for k in keys};records=[]
 b={k:q.arr(R/'shared-output-v2'/f'{k}-candidate.png') for k in keys}
 old=np.concatenate([np.concatenate([b['r09_c11'][-627:,-627:],b['r09_c12'][-627:,:627]],axis=1),np.concatenate([b['r10_c11'][:627,-627:],b['r10_c12'][:627,:627]],axis=1)],axis=0)
 src=R/'corner-joint/native/s1.png';new=q.arr(src);_,mask,fields=patch(old,new,'corner')
 rep,rec=recordpatch(R/'corner-joint/output-v2',src,old,new,mask,fields,[44429,36237],'corner-return',[R/'shared-output-v2'/f'{k}-candidate.png' for k in keys]);records.append(rec);old[mask]=rep[mask]
 a['r09_c11'][-627:,-627:]=old[:627,:627];a['r09_c12'][-627:,:627]=old[:627,627:];a['r10_c11'][:627,-627:]=old[627:,:627];a['r10_c12'][:627,:627]=old[627:,627:]
 old=a['r10_c11'][2445:3699,2842:4096].copy();src=R/'east-joint/native/s4-left-return.png';new=q.arr(src);cost=np.mean(abs(old-new),axis=2);yy,xx=np.mgrid[:1254,:1254];right=q.path(cost[:,850:1020])+850;bottom=q.path(cost[820:1010].T)+820
 mask=(xx<right[:,None])&(yy<bottom[None,:])
 rep,rec=recordpatch(R/'east-joint/output-v4',src,old,new,mask,{'right':right,'bottom':bottom},[43802,39309],'leaf-L-return',[inp/'r10_c11-candidate.png']);records.append(rec);a['r10_c11'][2445:3699,2842:4096][mask]=rep[mask]
 for k in keys:save(a[k],out/f'{k}-candidate.png',[inp/f'{k}-candidate.png']+[Path(x['replacement']) for x in records],{'method':'exact native patch replacement','formalAccepted':False})
 h.p.write(out/'record.json',{'inputStage':str(inp),'repairs':records,'formalAccepted':False})
 north=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0);east=np.concatenate([a['r10_c11'][:,-627:],a['r10_c12'][:,:627]],axis=1)
 for axis,v in [('north',north),('east',east)]:
  for i,x in enumerate([0,1024,2048,2842],1):save(v[:,x:x+1254] if axis=='north' else v[x:x+1254],out/f'{axis}-s{i}-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 shared-edge and return review'})
 whole=Image.new('RGB',(8192,8192))
 for k,(x,y) in zip(keys,[(0,0),(4096,0),(0,4096),(4096,4096)]):whole.paste(Image.open(out/f'{k}-candidate.png'),(x,y))
 outer=whole.crop((3200,3200,4992,4992));board=Image.new('RGB',(1024,1024))
 for box,pos in zip([(13,640,525,1152),(1267,640,1779,1152),(640,13,1152,525),(640,1267,1152,1779)],[(0,0),(512,0),(0,512),(512,512)]):board.paste(outer.crop(box),pos)
 board.save(out/'corner-edges-native.png');whole.crop((3469,3469,4723,4723)).save(out/'corner-review.png')
 tile=Image.open(out/'r10_c11-candidate.png');tile.crop((2842,2445,4096,3699)).save(out/'leaf-return-review.png')
 board=Image.new('RGB',(1024,1024))
 for box,pos in zip([(2586,2816,3098,3328),(3410,2816,3922,3328),(2830,2189,3342,2701),(3098,3195,3610,3707)],[(0,0),(512,0),(0,512),(512,512)]):board.paste(tile.crop(box),pos)
 board.save(out/'leaf-edges-native.png')
 q.qa(tile,'shared-v4',out/'r10_c11-candidate.png')
 print(str(out))
if __name__=='__main__':run()

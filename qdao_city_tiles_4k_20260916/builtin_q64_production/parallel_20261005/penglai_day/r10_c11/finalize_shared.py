from pathlib import Path
import sys,numpy as np
from PIL import Image,ImageFilter
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T));import internal_qa as q
from merge_shared import save
h=q.h

def patch(old,new,kind):
 yy,xx=np.mgrid[:1254,:1254];cost=np.mean(abs(old-new),axis=2)
 if kind=='wall':
  top=q.path(cost[80:180].T)+80;bottom=q.path(cost[1120:1240].T)+1120;left=q.path(cost[:,760:850])+760;right=q.path(cost[:,1220:1254])+1220;mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None])
 else:
  top=q.path(cost[250:420].T)+250;bottom=q.path(cost[850:1030].T)+850;left=q.path(cost[:,330:480])+330;right=q.path(cost[:,800:960])+800;mask=((yy>=top[None,:])&(yy<bottom[None,:]))|((xx>=left[:,None])&(xx<right[:,None]))
 w=np.clip((1-np.asarray(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.GaussianBlur(32)),dtype=np.float32)/255)*2,0,1)*mask;field=np.clip(q.smooth2(old-new,12),-12,12)*w[:,:,None];return new+field,mask,{'top':top,'bottom':bottom,'left':left,'right':right,'field':field}

def run():
 inp=R/'shared-output-v2';out=R/'shared-output-v3';out.mkdir(exist_ok=True);keys=['r09_c11','r09_c12','r10_c11','r10_c12'];a={k:q.arr(inp/f'{k}-candidate.png') for k in keys};records=[]
 north=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0);old=north[:,2048:3302].copy();src=R/'north-joint/native/s3-returnfix.png';rep,mask,fields=patch(old,q.arr(src),'wall');north[:,2048:3302][mask]=rep[mask];a['r09_c11'][-627:]=north[:627];a['r10_c11'][:627]=north[627:];d=R/'north-joint/output-v3';d.mkdir(exist_ok=True);rp=d/'wall-return-replacement.png';mp=d/'wall-return-mask.png';fp=d/'wall-return-fields.npz';save(rep,rp,[src,inp/'r09_c11-candidate.png',inp/'r10_c11-candidate.png'],{'method':'native AI wall-return repair with bounded12 RGB perimeter correction','geometricShift':0,'resampling':False,'imageBlur':False});Image.fromarray(mask.astype('uint8')*255).save(mp);np.savez_compressed(fp,**fields);h.p.derived(mp,[rp],{'method':'binary ownership in native1254 wall return'});records.append({'name':'wallReturn','source':str(src),'replacement':str(rp),'mask':str(mp),'fields':str(fp),'globalOriginXY':[43008,36237]})
 corner=np.concatenate([np.concatenate([a['r09_c11'][-627:,-627:],a['r09_c12'][-627:,:627]],axis=1),np.concatenate([a['r10_c11'][:627,-627:],a['r10_c12'][:627,:627]],axis=1)],axis=0);src=R/'corner-joint/native/s1.png';rep,mask,fields=patch(corner,q.arr(src),'corner');corner[mask]=rep[mask];a['r09_c11'][-627:,-627:]=corner[:627,:627];a['r09_c12'][-627:,:627]=corner[:627,627:];a['r10_c11'][:627,-627:]=corner[627:,:627];a['r10_c12'][:627,:627]=corner[627:,627:];d=R/'corner-joint/output-v1';d.mkdir(exist_ok=True);rp=d/'replacement.png';mp=d/'mask.png';fp=d/'fields.npz';save(rep,rp,[src]+[inp/f'{k}-candidate.png' for k in keys],{'method':'native AI fourtile-corner cross repair with bounded12 RGB perimeter correction','geometricShift':0,'resampling':False,'imageBlur':False});Image.fromarray(mask.astype('uint8')*255).save(mp);np.savez_compressed(fp,**fields);h.p.derived(mp,[rp],{'method':'binary cross mask from minimum-error native paths'});records.append({'name':'fourTileCorner','source':str(src),'replacement':str(rp),'mask':str(mp),'fields':str(fp),'globalOriginXY':[44429,36237]})
 for k in keys:save(a[k],out/f'{k}-candidate.png',[inp/f'{k}-candidate.png']+[Path(e['replacement']) for e in records],{'method':'native exact masks split over tile boundaries','formalAccepted':False})
 h.p.write(out/'record.json',{'inputStage':str(inp),'repairs':records,'formalAccepted':False})
 north=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0);east=np.concatenate([a['r10_c11'][:,-627:],a['r10_c12'][:,:627]],axis=1)
 for axis,v in [('north',north),('east',east)]:
  for i,x in enumerate([0,1024,2048,2842],1):save(v[:,x:x+1254] if axis=='north' else v[x:x+1254],out/f'{axis}-s{i}-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 shared-edge and return review'})
 save(corner,out/'corner-review.png',[out/f'{k}-candidate.png' for k in keys],{'method':'native1254 fourtile corner review'})
 # Bigger native context verifies all four patch-edge returns without resampling.
 whole=Image.new('RGB',(8192,8192))
 for k,(x,y) in zip(keys,[(0,0),(4096,0),(0,4096),(4096,4096)]):whole.paste(Image.open(out/f'{k}-candidate.png'),(x,y))
 for name,box in [('corner-outer',(3200,3200,4992,4992)),('east-left-return',(3240,2810,3980,3350)),('wall-upper-return',(2780,3360,3440,3840))]:
  p=out/f'{name}.png';whole.crop(box).save(p);h.p.derived(p,[out/f'{k}-candidate.png' for k in keys],{'method':'native exact global-context QA','quadBoxLTRB':box})
 q.qa(Image.open(out/'r10_c11-candidate.png'),'shared-v3',out/'r10_c11-candidate.png')
if __name__=='__main__':run()

from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T));import internal_qa as q
h=q.h;starts=[0,1024,2048,2842]
names={'north':['s1-edgefix','s2-seamfix','s3','s4-seamfix'],'east':['s1','s2','s3-seamfix','s4']}
def save(im,p,sources,op):
 Image.fromarray(np.clip(np.rint(im),0,255).astype('uint8')).save(p);h.p.derived(p,sources,op)
def compose():
 state=h.p.read(R/'shared-boundary-state.json');a={k:q.arr(v['file']) for k,v in state.items()};records=[]
 for axis in ['north','east']:
  d=R/(axis+'-joint');(d/'output-v2').mkdir(exist_ok=True);o=d/'output-v2';sources=[Path(state[k]['file']) for k in (['r09_c11','r10_c11'] if axis=='north' else ['r10_c11','r10_c12'])];joint=np.concatenate([a['r09_c11'][-627:],a['r10_c11'][:627]],axis=0) if axis=='north' else np.concatenate([a['r10_c11'][:,-627:],a['r10_c12'][:,:627]],axis=1).transpose(1,0,2)
  yy,xx=np.mgrid[:1254,:1254]
  for i,(name,x) in enumerate(zip(names[axis],starts),1):
   p=d/'native'/f'{name}.png';new=q.arr(p);new=new if axis=='north' else new.transpose(1,0,2);old=joint[:,x:x+1254].copy();cost=np.mean(abs(old-new),axis=2)
   top=q.path(cost[220:380].T)+220;bottom=q.path(cost[930:1120].T)+930;left=np.zeros(1254,np.int16) if i==1 else q.path(cost[:,80:260])+80;right=np.full(1254,1254,np.int16) if i==4 else q.path(cost[:,1130:1240])+1130
   if axis=='east' and i==3:top=q.path(cost[50:170].T)+50
   if axis=='east' and i==4:top=q.path(cost[0:70].T)
   mask=(yy>=top[None,:])&(yy<bottom[None,:])&(xx>=left[:,None])&(xx<right[:,None]);dist=np.minimum(yy-top[None,:],bottom[None,:]-yy)
   if i>1:dist=np.minimum(dist,xx-left[:,None])
   if i<4:dist=np.minimum(dist,right[:,None]-xx)
   w=np.clip(1-dist/110,0,1)**2*mask;field=np.clip(q.smooth2(old-new,12),-12,12)*w[:,:,None];rep=new+field;joint[:,x:x+1254][mask]=rep[mask]
   if axis=='east':rep=rep.transpose(1,0,2);mask=mask.T;field=field.transpose(1,0,2)
   rp=o/f's{i}-replacement.png';mp=o/f's{i}-mask.png';fp=o/f's{i}-fields.npz';np.savez_compressed(fp,field=field,normalTop=top,normalBottom=bottom,tangentLeft=left,tangentRight=right);save(rep,rp,[p]+sources,{'method':'bounded12 RGB return field applied to nativeAI source, no geometric shift/resample/blur/feather','fields':str(fp)});Image.fromarray(mask.astype('uint8')*255).save(mp);h.p.derived(mp,[p]+sources,{'method':'binary min-error source ownership in native overlap','coordinates':'native orientation'});sources += [rp,mp];records.append({'axis':axis,'segment':i,'source':str(p),'replacement':str(rp),'mask':str(mp),'originInJointXY':[x,0] if axis=='north' else [0,x],'fields':str(fp)})
  native=joint if axis=='north' else joint.transpose(1,0,2);jp=o/'joint.png';save(native,jp,sources,{'method':'native shared edge assembled with precise masks','globalRectXYWH':[40960,36237,4096,1254] if axis=='north' else [44429,36864,1254,4096]})
  for i,x in enumerate(starts,1):save(native[:,x:x+1254] if axis=='north' else native[x:x+1254],o/f's{i}-review.png',[jp],{'method':'native1254 shared-edge and return QA'})
  if axis=='north':a['r09_c11'][-627:]=joint[:627];a['r10_c11'][:627]=joint[627:]
  else:a['r10_c11'][:,-627:]=native[:,:627];a['r10_c12'][:,:627]=native[:,627:]
  h.p.write(o/'record.json',{'axis':axis,'repairs':[e for e in records if e['axis']==axis],'formalAccepted':False})
 out=R/'shared-output-v2';out.mkdir(exist_ok=True)
 for k,im in a.items():save(im,out/f'{k}-candidate.png',[Path(state[k]['file'])]+[Path(e['replacement']) for e in records],{'method':'joint split at exact shared axes','formalAccepted':False})
 corner=np.concatenate([np.concatenate([a['r09_c11'][-627:,-627:],a['r09_c12'][-627:,:627]],axis=1),np.concatenate([a['r10_c11'][:627,-627:],a['r10_c12'][:627,:627]],axis=1)],axis=0);save(corner,out/'corner-target.png',[out/f'{k}-candidate.png' for k in a],{'method':'native fourtile1254corner','globalRectXYWH':[44429,36237,1254,1254]});h.p.write(out/'record.json',{'sources':state,'repairs':records,'formalAccepted':False})
if __name__=='__main__':compose()

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
def run():
 state=h.p.read(R/'shared-boundary-state.json');a={k:q.arr(v['file']) for k,v in state.items()};records=[]
 for v in state.values():assert h.p.sha(v['file'])==v['sha256']
 src=R/'internal-ai/native/shadow.png';origin=[2445,397];x,y=origin
 out,e=record(R/'internal-ai/output-v1','shadow',a['r10_c10'][y:y+1254,x:x+1254],q.arr(src),src,origin,[(280,410),(1080,1190),(200,340),(1170,1254)])
 a['r10_c10'][y:y+1254,x:x+1254]=out;e['tile']='r10_c10';records.append(e)
 internal=R/'internal-ai/r10_c10-internal-v3.png';save(a['r10_c10'],internal,[state['r10_c10']['file'],e['replacement']],{'method':'internal shadow exact mask patch'});q.qa(Image.fromarray(a['r10_c10'].astype('uint8')),'internal-v3',internal)
 names={'north':['s1','s2','s3','s4-fix'],'east':['s1','s2-fix','s3-fix','s4']}
 for axis in ['north','east']:
  d=R/(axis+'-joint');o=d/'output-v1';o.mkdir(exist_ok=True)
  joint=np.concatenate([a['r09_c10'][-627:],a['r10_c10'][:627]],0) if axis=='north' else np.concatenate([a['r10_c10'][:,-627:],a['r10_c11'][:,:627]],1).transpose(1,0,2)
  for i,(name,x) in enumerate(zip(names[axis],starts),1):
   src=d/'native'/(name+'.png');new=q.arr(src);new=new if axis=='north' else new.transpose(1,0,2)
   old=joint[:,x:x+1254].copy();bands=[(220,380),(950,1130),0 if i==1 else ((100,390) if i==4 else (80,220)),1254 if i==4 else (1150,1240)]
   out,e=record(o,f's{i}',old,new,src,[x,0] if axis=='north' else [0,x],bands,axis=='east');joint[:,x:x+1254]=out;e['axis']=axis;e['segment']=i;records.append(e)
  native=joint if axis=='north' else joint.transpose(1,0,2);fp=o/'joint.png';save(native,fp,[e['replacement'] for e in records if e.get('axis')==axis],{'method':'native sharededge composed by precisebinarymask'})
  for i,x in enumerate(starts,1):save(native[:,x:x+1254] if axis=='north' else native[x:x+1254],o/f's{i}-review.png',[fp],{'method':'native1254 return context QA'})
  if axis=='north':a['r09_c10'][-627:]=joint[:627];a['r10_c10'][:627]=joint[627:]
  else:a['r10_c10'][:,-627:]=native[:,:627];a['r10_c11'][:,:627]=native[:,627:]
 O=R/'shared-output-v1';O.mkdir(exist_ok=True)
 for k,v in a.items():save(v,O/(k+'-candidate.png'),[state[k]['file']]+[e['replacement'] for e in records],{'method':'native joint split; neighbor candidates are local-only proposals'})
 corner=np.concatenate([np.concatenate([a['r09_c10'][-627:,-627:],a['r09_c11'][-627:,:627]],1),np.concatenate([a['r10_c10'][:627,-627:],a['r10_c11'][:627,:627]],1)],0)
 D=R/'corner-joint';D.mkdir(exist_ok=True)
 for n in ['native','prompts','evidence']:(D/n).mkdir(exist_ok=True)
 save(corner,D/'corner-target.png',[O/(k+'-candidate.png') for k in a],{'method':'native fourtile1254corner','globalRectXYWH':[40333,36237,1254,1254]})
 h.p.write(O/'record.json',{'sources':state,'repairs':records,'candidateOnly':True})
if __name__=='__main__':run()


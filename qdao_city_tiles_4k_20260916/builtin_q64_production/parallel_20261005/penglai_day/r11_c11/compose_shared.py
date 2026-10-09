from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
q=c.q;h=c.h;R=T/'repairs';state=h.p.read(R/'shared-boundary-state.json');a={k:q.arr(v['file']) for k,v in state.items()};records=[]
for v in state.values():assert h.p.sha(v['file'])==v['sha256']
names={'north':['s1','s2-gap','s3-gap','s4-gap'],'west':['s1-gap','s2-gap','s3-gap','s4-gap']}
for axis in ['north','west']:
 d=R/(axis+'-joint');o=d/'output-v1';o.mkdir(exist_ok=True)
 joint=np.concatenate([a['r10_c11'][-627:],a['r11_c11'][:627]],0) if axis=='north' else np.concatenate([a['r11_c10'][:,-627:],a['r11_c11'][:,:627]],1).transpose(1,0,2)
 for i,(name,x) in enumerate(zip(names[axis],c.starts),1):
  src=d/'native'/(name+'.png');new=q.arr(src);new=new if axis=='north' else new.transpose(1,0,2)
  old=joint[:,x:x+1254].copy();bands=[(200,380),(950,1130),0 if i==1 else ((80,180) if i==4 else (40,160)),1254 if i==4 else (1160,1240)]
  if axis=='north' and i==3:bands[1]=1254
  if axis=='north' and i==4:bands[0]=0
  if axis=='west' and i in [2,3]:bands[1]=(700,747)
  out,e=c.record(o,f's{i}',old,new,src,[x,-627] if axis=='north' else [-627,x],bands,axis=='west');joint[:,x:x+1254]=out;e['axis']=axis;e['segment']=i;records.append(e)
  h.p.derived(e['mask'],[src,state['r11_c11']['file']],{'method':'binary native minimum error source ownership','bands':bands,'fields':e['fields'],'axis':axis,'transpose':axis=='west'})
 native=joint if axis=='north' else joint.transpose(1,0,2);fp=o/'joint.png';c.save(native,fp,[e['replacement'] for e in records if e['axis']==axis],{'method':'native sharededge composed by precisebinarymask'})
 for i,x in enumerate(c.starts,1):c.save(native[:,x:x+1254] if axis=='north' else native[x:x+1254],o/f's{i}-review.png',[fp],{'method':'native1254 return context QA'})
 for i,x in enumerate([1024,2048,3072],1):c.save(native[:,x-627:x+627] if axis=='north' else native[x-627:x+627],o/f'cross{i}-review.png',[fp],{'method':'native1254 segment crossing context'})
 if axis=='north':a['r10_c11'][-627:]=joint[:627];a['r11_c11'][:627]=joint[627:]
 else:a['r11_c10'][:,-627:]=native[:,:627];a['r11_c11'][:,:627]=native[:,627:]
O=R/'shared-output-v1';O.mkdir(exist_ok=True)
for k,v in a.items():c.save(v,O/(k+'-candidate.png'),[state[k]['file']]+[e['replacement'] for e in records],{'method':'native joint split; neighbor candidates are local-only proposals'})
corner=np.concatenate([np.concatenate([a['r10_c10'][-627:,-627:],a['r10_c11'][-627:,:627]],1),np.concatenate([a['r11_c10'][:627,-627:],a['r11_c11'][:627,:627]],1)],0)
D=R/'corner-joint';D.mkdir(exist_ok=True)
for n in ['native','prompts','evidence']:(D/n).mkdir(exist_ok=True)
c.save(corner,D/'corner-target.png',[O/(k+'-candidate.png') for k in a],{'method':'native fourtile1254corner','globalRectXYWH':[40333,40333,1254,1254]})
h.p.write(O/'record.json',{'sources':state,'repairs':records,'candidateOnly':True})


from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
q=c.q;h=c.h;R=T/'repairs';D=R/'north-joint';state=h.p.read(R/'shared-boundary-state.json');a={k:q.arr(v['file']) for k,v in state.items()}
for v in state.values():assert h.p.sha(v['file'])==v['sha256']
joint=np.concatenate([a['r10_c10'][-627:],a['r11_c10'][:627]],0);records=[]
for i,x in enumerate([0,1024,2048,2842],1):
 src=D/'native'/f's{i}.png';bands=[(200,380),(950,1130),0 if i==1 else ((100,390) if i==4 else (80,220)),1254 if i==4 else (1150,1240)]
 out,e=c.record(D/'output-v1',f's{i}',joint[:,x:x+1254],q.arr(src),src,[x,0],bands);joint[:,x:x+1254]=out;records.append(e)
O=R/'shared-output-v1';O.mkdir(exist_ok=True);fp=O/'north-joint.png';c.save(joint,fp,[e['replacement'] for e in records],{'method':'native sharededge compose binarymask','globalRectXYWH':[36864,40333,4096,1254]})
a['r10_c10'][-627:]=joint[:627];a['r11_c10'][:627]=joint[627:]
for k,v in a.items():c.save(v,O/(k+'-candidate.png'),[state[k]['file']]+[e['replacement'] for e in records],{'method':'native joint split; neighbor delta proposal only'})
for i,x in enumerate([0,1024,2048,2842],1):c.save(joint[:,x:x+1254],O/f'north-s{i}-review.png',[fp],{'method':'native1254 fullreturncontext'})
for i,x in enumerate([1024,2048,3072],1):c.save(joint[:,x-627:x+627],O/f'north-cross{i}-review.png',[fp],{'method':'native1254 segment crossing context'})
f=O/'r11_c10-candidate.png';im=Image.open(f);q.qa(im,'shared-v1',f)
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:
  box=(x-627,y-627,x+627,y+627);dest=O/f'internal-full-{x}-{y}.png';im.crop(box).save(dest);h.p.derived(dest,[f],{'method':'native1254 finalinternal context','boxLTRB':box})
im.resize((1254,1254),Image.Resampling.LANCZOS).save(O/'preview.png')
h.p.write(O/'record.json',{'sources':state,'repairs':records,'formalAccepted':False})


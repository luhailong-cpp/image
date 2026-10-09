from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_shared as c
q=c.q;h=c.h;R=T/'repairs';I=R/'shared-output-v1';O=R/'shared-output-v2';O.mkdir(exist_ok=True)
names=['r09_c10','r09_c11','r10_c10','r10_c11'];a={k:q.arr(I/(k+'-candidate.png')) for k in names}
records=[]
src=R/'internal-ai/native/shadow-return.png';x,y=2842,397;old=a['r10_c10'][y:y+1254,x:x+1254]
out,e=c.record(R/'internal-ai/output-v2','shadow-return',old,q.arr(src),src,[x,y],[(570,610),(740,800),(680,740),(900,950)])
a['r10_c10'][y:y+1254,x:x+1254]=out;e['tile']='r10_c10';records.append(e)
old=np.concatenate([np.concatenate([a['r09_c10'][-627:,-627:],a['r09_c11'][-627:,:627]],1),np.concatenate([a['r10_c10'][:627,-627:],a['r10_c11'][:627,:627]],1)],0)
src=R/'corner-joint/native/corner.png';out,e=c.record(R/'corner-joint/output-v2','corner',old,q.arr(src),src,[40333,36237],[0,1254,0,1254]);records.append(e)
a['r09_c10'][-627:,-627:]=out[:627,:627];a['r09_c11'][-627:,:627]=out[:627,627:];a['r10_c10'][:627,-627:]=out[627:,:627];a['r10_c11'][:627,:627]=out[627:,627:]
for k,v in a.items():c.save(v,O/(k+'-candidate.png'),[I/(k+'-candidate.png')]+[e['replacement'] for e in records],{'method':'exactmask shadow-return and fourtilecorner nativeAI','formalAccepted':False})
h.p.write(O/'record.json',{'parent':str(I/'record.json'),'repairs':records})
def crop(box):
 canvas=Image.new('RGB',(1254,1254));pos={'r09_c10':(0,-4096),'r09_c11':(4096,-4096),'r10_c10':(0,0),'r10_c11':(4096,0)}
 for k,(x,y) in pos.items():
  inter=[max(box[0],x),max(box[1],y),min(box[2],x+4096),min(box[3],y+4096)]
  if inter[2]>inter[0] and inter[3]>inter[1]:
   im=Image.fromarray(a[k].astype('uint8')).crop((inter[0]-x,inter[1]-y,inter[2]-x,inter[3]-y));canvas.paste(im,(inter[0]-box[0],inter[1]-box[1]))
 return canvas
for n,(x,y) in {'corner':(4096,0),'left-return':(3469,0),'top-return':(4096,-627),'right-return':(4723,0),'bottom-return':(4096,627),'shadow-return':(3469,1024)}.items():
 im=crop([x-627,y-627,x+627,y+627]);fp=O/(n+'-review.png');im.save(fp);h.p.derived(fp,[O/(k+'-candidate.png') for k in names],{'method':'native1254 contextQA','globalCenter':[36864+x,36864+y]})
for axis in ['north','east']:
 joint=np.concatenate([a['r09_c10'][-627:],a['r10_c10'][:627]],0) if axis=='north' else np.concatenate([a['r10_c10'][:,-627:],a['r10_c11'][:,:627]],1)
 for i,x in enumerate(c.starts,1):c.save(joint[:,x:x+1254] if axis=='north' else joint[x:x+1254],O/f'{axis}-s{i}-review.png',[O/(k+'-candidate.png') for k in names],{'method':'final native1254 sharededge segment QA'})
im=Image.fromarray(a['r10_c10'].astype('uint8'));q.qa(im,'shared-v2',O/'r10_c10-candidate.png');im.resize((1254,1254),Image.Resampling.LANCZOS).save(O/'preview.png')


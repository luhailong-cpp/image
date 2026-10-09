from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
h=c.h;R=T/'repairs';I=R/'shared-output-v1';D=R/'corner-joint';O=R/'shared-output-v2';O.mkdir(exist_ok=True)
record=h.p.read(I/'record.json');a={k:c.q.arr(I/(k+'-candidate.png')) for k in record['sources']}
old=c.q.arr(D/'corner-target.png');src=D/'native/corner-gap.png';bands=[(250,350),(1120,1240),(250,400),(1120,1250)]
out,e=c.record(D/'output-v1','corner',old,c.q.arr(src),src,[-627,-627],bands)
h.p.derived(e['mask'],[src,D/'corner-target.png'],{'method':'binary fourtile nativeAI ownership','bands':bands,'fields':e['fields']})
c.save(out,D/'output-v1/corner-review.png',[D/'corner-target.png',e['replacement'],e['mask']],{'method':'native1254 fourtile fullreturn context'})
a['r10_c10'][-627:,-627:]=out[:627,:627];a['r10_c11'][-627:,:627]=out[:627,627:];a['r11_c10'][:627,-627:]=out[627:,:627];a['r11_c11'][:627,:627]=out[627:,627:]
record['repairs'].append(e)
for k,v in a.items():c.save(v,O/(k+'-candidate.png'),[I/(k+'-candidate.png'),e['replacement'],e['mask']],{'method':'nativefourcorner exactsplit; localproposalonly'})
h.p.write(O/'record.json',record)
for axis in ['north','west']:
 ar=np.concatenate([a['r10_c11'][-627:],a['r11_c11'][:627]],0) if axis=='north' else np.concatenate([a['r11_c10'][:,-627:],a['r11_c11'][:,:627]],1)
 fp=O/(axis+'-joint.png');c.save(ar,fp,[O/(k+'-candidate.png') for k in a],{'method':'nativejoint final review'})
 for i,x in enumerate(c.starts,1):c.save(ar[:,x:x+1254] if axis=='north' else ar[x:x+1254],O/f'{axis}-s{i}-review.png',[fp],{'method':'native1254 sharededge return'})
 for i,x in enumerate([1024,2048,3072],1):c.save(ar[:,x-627:x+627] if axis=='north' else ar[x-627:x+627],O/f'{axis}-cross{i}-review.png',[fp],{'method':'native1254 overlap return'})
im=Image.open(O/'r11_c11-candidate.png');c.q.qa(im,'shared-v2',O/'r11_c11-candidate.png')
p=O/'preview.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(p);h.p.derived(p,[O/'r11_c11-candidate.png'],{'method':'review only downscale'})


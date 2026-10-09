from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
q=c.q;h=c.h;R=T/'repairs';D=R/'internal-ai';state=h.p.read(D/'targets.json');a=q.arr(state['source']);records=[]
bands={'stone-upper':[(200,340),(1130,1210),(300,440),(860,1000)],'stone-lower':[(290,440),(790,880),(550,625),(1100,1220)],'leaf':[(250,340),(770,840),(0,50),(1190,1254)],'post':[(390,460),(760,810),(650,685),(880,925)]}
for n,(x,y) in state['origins'].items():
 src=D/'native'/(n+'.png');out,e=c.record(D/'output-v1',n,a[y:y+1254,x:x+1254],q.arr(src),src,[x,y],bands[n]);a[y:y+1254,x:x+1254]=out;records.append(e)
out=R/'internal-v3.png';c.save(a,out,[state['source']]+[r['replacement'] for r in records],{'method':'exact binary localAI repair with bounded12 RGB fields'});h.p.write(D/'output-v1/record.json',{'source':state,'candidate':str(out),'candidateSHA':h.p.sha(out),'repairs':records});im=Image.fromarray(a.astype('uint8'));q.qa(im,'internal-v3',out)
for n,(x,y) in state['origins'].items():c.save(a[y:y+1254,x:x+1254],D/'output-v1'/(n+'-review.png'),[out],{'method':'native1254 full return context'})
im.resize((1254,1254),Image.Resampling.LANCZOS).save(R/'internal-v3-preview.png')
# freeze shared north inputs
st=h.p.read(T/'evidence/boundary-state.json');north=st['north'];assert h.p.sha(north['source'])==north['sha256'];ns={'r10_c10':{'file':north['source'],'sha256':north['sha256']},'r11_c10':{'file':str(out),'sha256':h.p.sha(out)}};h.p.write(R/'shared-boundary-state.json',ns)
D=R/'north-joint';D.mkdir(exist_ok=True)
for n in ['native','prompts','evidence']:(D/n).mkdir(exist_ok=True)
joint=np.concatenate([q.arr(north['source'])[-627:],a[:627]],0)
for i,x in enumerate([0,1024,2048,2842],1):c.save(joint[:,x:x+1254],D/f's{i}-target.png',[north['source'],out],{'method':'native1254 sharededge target','originInJoint':[x,0],'globalRectXYWH':[36864+x,40333,1254,1254]})


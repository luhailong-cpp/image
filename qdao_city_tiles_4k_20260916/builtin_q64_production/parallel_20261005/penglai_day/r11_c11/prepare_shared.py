from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
h=c.h;R=T/'repairs';state=h.p.read(T/'evidence/boundary-state.json')
sources={'r10_c11':state['north']['source'],'r11_c11':str(R/'r11_c11-internal-v3.png'),'r11_c10':state['west']['source'],'r10_c10':state['northwest']['source']}
for v in state.values():
 if isinstance(v,dict):assert h.p.sha(v['source'])==v['sha256']
h.p.write(R/'shared-boundary-state.json',{k:{'file':v,'sha256':h.p.sha(v)} for k,v in sources.items()})
a={k:c.q.arr(v) for k,v in sources.items()}
for axis in ['north','west']:
 d=R/(axis+'-joint');d.mkdir(exist_ok=True)
 for name in ['native','evidence','prompts']:(d/name).mkdir(exist_ok=True)
 ar=np.concatenate([a['r10_c11'][-627:],a['r11_c11'][:627]],0) if axis=='north' else np.concatenate([a['r11_c10'][:,-627:],a['r11_c11'][:,:627]],1)
 for i,x in enumerate([0,1024,2048,2842],1):
  im=ar[:,x:x+1254] if axis=='north' else ar[x:x+1254];f=d/f's{i}-target.png';c.save(im,f,[sources['r11_c11'],sources['r10_c11' if axis=='north' else 'r11_c10']],{'method':'native1254 sharededge target','axis':axis,'tangentStart':x,'seamAt':627})

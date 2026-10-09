from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import internal_qa as q
h=q.h;R=T/'repairs'
def setup():
 state=h.p.read(T/'evidence/boundary-state.json')
 sources={'r09_c10':state['north']['source'],'r10_c10':str(R/'internal-quilt/r10_c10-internal-v2.png'),'r10_c11':state['east']['source'],'r09_c11':str(T.parent/'tiles/current/region-v4/r09_c11-candidate.png')}
 assert h.p.sha(sources['r09_c11'])=='7d09162b09c97916cf4b73c2f539e6da05a9cbe5f5a0f5c793cb0fd5f49a7d22'
 h.p.write(R/'shared-boundary-state.json',{k:{'file':v,'sha256':h.p.sha(v)} for k,v in sources.items()})
 a={k:q.arr(v).astype('uint8') for k,v in sources.items()}
 for axis in ['north','east']:
  d=R/(axis+'-joint');d.mkdir(exist_ok=True)
  for name in ['native','evidence','prompts']:(d/name).mkdir(exist_ok=True)
  ar=np.concatenate([a['r09_c10'][-627:],a['r10_c10'][:627]],0) if axis=='north' else np.concatenate([a['r10_c10'][:,-627:],a['r10_c11'][:,:627]],1)
  for i,x in enumerate([0,1024,2048,2842],1):
   im=ar[:,x:x+1254] if axis=='north' else ar[x:x+1254];f=d/f's{i}-target.png';Image.fromarray(im).save(f);h.p.derived(f,list(sources.values()),{'method':'native1254 sharededge target','axis':axis,'tangentStart':x})
 d=R/'internal-ai';d.mkdir(exist_ok=True)
 for name in ['native','evidence','prompts']:(d/name).mkdir(exist_ok=True)
 src=R/'internal-quilt/r10_c10-internal-v2.png';f=d/'shadow-target.png';Image.open(src).crop((2445,397,3699,1651)).save(f);h.p.derived(f,[src],{'method':'native1254crop','box':[2445,397,3699,1651]})
def prepare(folder,name,detail):
 d=R/folder;target=d/(name+'-target.png');refs=[target.as_posix(),h.STYLE]
 prompt='Use case: precise native map repair. Image1 is the exact EDIT TARGET, native1254 square. Image2 approved painting style only; no UI. '+detail+' Keep identical1254 crop, camera, object counts, architecture, leaf cluster silhouettes, main shapes, edge endpoints and material painting. Repair only the described artificial seams and their connected contours; retain all other pixels and outer200px context as faithfully as possible. Bright clean rounded Taoist Q fantasy handpainting, warm highlights/cool shadows, restrained smooth texture. No new objects, cracks, branches, denser foliage, grain, sharpening, blur or feathering. Reconcile material differences by painting coherent original details.'
 call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};h.p.write(d/'prompts'/(name+'.call.json'),call);(d/'prompts'/(name+'.prompt.txt')).write_text(prompt,encoding='utf8');print(json.dumps(call))
def ingest(folder,name,source):
 d=R/folder;h.p.ROOT=d;call=h.p.read(d/'prompts'/(name+'.call.json'));dest=h.p.ingest(source,name,d/'prompts'/(name+'.prompt.txt'),call['referenced_image_paths'],'native_ai_shared_or_internal_repair');rec=h.p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['evidence']['toolOutputHintFile']=str(d/'evidence'/(name+'.tool-result.json'));h.p.write(str(dest)+'.generation.json',rec)
if __name__=='__main__':
 if sys.argv[1]=='setup':setup()
 elif sys.argv[1]=='prepare':prepare(*sys.argv[2:])
 elif sys.argv[1]=='ingest':ingest(*sys.argv[2:])


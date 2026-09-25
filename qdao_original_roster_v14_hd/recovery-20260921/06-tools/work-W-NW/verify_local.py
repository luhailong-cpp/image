from pathlib import Path
import importlib.util,json,hashlib,sys
from PIL import Image
import numpy as np
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent;OUT=HERE/'candidate/06_thunder_caster_boy'
sys.path.insert(0,str(PARENT));import alpha_verify as v
original_root=v.ROOT
def module(n):
 spec=importlib.util.spec_from_file_location(n,original_root/'tools/vendor'/f'{n}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
v.ROOT=HERE;v.mod=module
results={d:v.verify('06_thunder_caster_boy',d) for d in ('W','NW')}
rows=[]
for d in ('W','NW'):
 for n in range(1,17):
  p=OUT/f'walk/{d}/{n:02d}.png';a=np.asarray(Image.open(p))[:,:,3];y,x=np.where(a>0);assert a.shape==(1024,1024) and a.min()==0 and a.max()==255
  assert not (np.any(a[0]) or np.any(a[-1]) or np.any(a[:,0]) or np.any(a[:,-1]))
  rows.append({'slot':f'{d}{n:02d}','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'all_alpha_bbox':[int(x.min()),int(y.min()),int(x.max())+1,int(y.max())+1]})
assert len(set(r['sha256'] for r in rows))==32
report={'scope':'W and NW only','directionResults':results,'files':rows,'pngs':32,'uniqueOutputHashes':32,'allAlphaCanvasEdgesClear':True,'modelVerified':False,'actualModel':None,'actualQuality':None,'paidApiCalls':0,'unityVerified':False}
(HERE/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pngs':32,'reconstructed':sum(r['reconstructed_frames'] for r in results.values()),'edges':'clear','unique':32}))

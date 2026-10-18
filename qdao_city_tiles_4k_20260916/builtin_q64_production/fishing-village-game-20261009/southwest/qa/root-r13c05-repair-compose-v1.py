import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
z=Path(__file__).resolve().parent.parent; q=z/'qa'; n=z/'native'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
jobs=read(q/'r13c05-repair-jobs-v1.json'); ap=q/'full-tile-r13_c05-assembly.json'; a=read(ap)
repairs=[]
for j in jobs:
 stem=j['stem']; p=n/(stem+'.png'); im=Image.open(p); assert im.size==(1254,1254)
 gp=n/(stem+'.png.generation.json')
 write(gp,{'tile':'r13_c05','type':'native_local_ai_repair','sha256':ref(p)['sha256'],'size':list(im.size),'builtin':True,'actualModel':None,'entryPoint':'image_gen.imagegen','request':j['request'],'receipt':ref(n/(stem+'.receipt.json')),'noUpscale':True})
 repairs.append({'id':stem.split('_')[2],'tileContextBox':j['tileContextBox'],'repairBounds':j['repairBounds'],'margin':j['margin'],'source':j['source'],'repair':ref(p),'generationRecord':ref(gp)})
mp=q/'repair-r13c05-v1-manifest.json'
write(mp,{'schemaVersion':1,'outputPrefix':'repair-r13c05-v1','baseAssembly':ref(ap),'expectedBaseCandidateSha256':a['output']['sha256'],'repairs':repairs})
subprocess.run([sys.executable,'-B',str(q/'repair-compose.py'),'--manifest',str(mp)],check=True)
trp=q/'repair-r13c05-v1-trace.json'; tr=read(trp)
out=Image.open(tr['candidate']['path']).convert('RGB'); ctx=Image.open(tr['context']['path']).convert('RGB')
old=np.asarray(Image.open(a['output']['path']).convert('RGB')); arr=np.asarray(out)
changed=np.any(old!=arr,axis=2)
changed_windows=[]; reused=[]; local=[]
for i,v in enumerate(a['qa']):
 l,t,r,b=v['sourceBox']
 if changed[t:b,l:r].any():
  p=q/Path(v['file']).name.replace('full-tile-r13_c05','repair-r13c05-v1')
  assert not p.exists();out.crop((l,t,r,b)).save(p)
  changed_windows.append({'index':i,'file':p.as_posix(),'sha256':ref(p)['sha256'],'sourceBox':v['sourceBox'],'source':tr['candidate'],'priorQa':v})
 else: reused.append({**v,'pixelUnchanged':True})
for j in jobs:
 box=[v+115 for v in j['tileContextBox']];p=q/('repair-r13c05-v1-'+j['stem']+'-composite-100pct.png')
 assert not p.exists();ctx.crop(box).save(p);local.append({'file':p.as_posix(),'sha256':ref(p)['sha256'],'contextBox':box})
qp=q/'repair-r13c05-v1-qa.json'
write(qp,{'tile':'r13_c05','trace':ref(trp),'candidate':tr['candidate'],'context':tr['context'],'changedWindows':changed_windows,'reused':reused,'local':local,'changedPixels':int(changed.sum()),'externalContextBordersUnchanged':all(np.array_equal(np.asarray(ctx)[sl],np.asarray(Image.open(a['context']['path']).convert('RGB'))[sl]) for sl in [(slice(0,230),slice(None)),(slice(-230,None),slice(None)),(slice(None),slice(0,230)),(slice(None),slice(-230,None))])})
print(json.dumps({'qa':ref(qp),'changedWindows':len(changed_windows),'reused':len(reused),'local':local}))

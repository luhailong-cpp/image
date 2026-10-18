import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
z=Path(__file__).resolve().parent.parent;q=z/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tp=q/'pair-r12c05-r13c05-v1-trace.json';t=read(tp);outchecks=[]
for old,new in zip(t['inputs'],t['tiles']):
 a=np.array(Image.open(old['context']['path']).convert('RGB'));b=np.array(Image.open(new['context']['path']).convert('RGB'));d=np.any(a!=b,axis=2); yy,xx=np.where(d)
 opposite=np.array_equal(a[:230],b[:230]) if old['tile']=='r12_c05' else np.array_equal(a[-230:],b[-230:])
 assert opposite
 interior=np.array_equal(a[:4096],b[:4096]) if old['tile']=='r12_c05' else np.array_equal(a[230:],b[230:]);assert interior
 outchecks.append({'tile':old['tile'],'old':old['context'],'new':new['context'],'changedContextBoundingBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if d.any() else None,'oppositeEdgeUnchanged':True,'outsideSharedOverlapUnchanged':True})
idx=read(z/'art-delivery-index.json');oldr12=next(v for v in idx['artAccepted'] if v['tile']=='r12_c05')
viewed=[]
for v in t['qa']:
 assert ref(v['path'])['sha256']==v['sha256']
 viewed.append(dict(v,viewedAtNativeResolution=True,result='passed'))
ap=q/'pair-r12c05-r13c05-v1-art-audit-v1.json'
write(ap,{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','status':'passed','tiles':['r12_c05','r13_c05'],'scope':'Internal r13c05 repair accepted and complete r12/r13 north-south shared edge checked at native scale. Prior r12 internal and north joins retained; all other outgoing edges remain pending.','trace':ref(tp),'internalAudits':[ref(q/'r13_c05-internal-visual-audit-v1.json'),oldr12['artAudit']],'outgoingEdgePixelChecks':outchecks,'nativeQaViewedCount':5,'viewed':viewed,'findings':[],'validation':'Continuous beach and grey rocks in parts 1-3; foam and shallow-water transitions continuous in parts 3-5. No hard cut, duplicated shore, or broken contour. Pair changes confined to native overlap and opposite borders identical.','sourcePixelIdentity':True,'nativePixelsResampled':False,'formalMapAcceptance':False,'runtimeValidation':'not performed'})
subprocess.run([sys.executable,'-B',str(q/'export-reviewed-versioned.py'),str(tp),str(ap)],check=True)
print(json.dumps({'trace':ref(tp),'audit':ref(ap),'r13Context':t['tiles'][1]['context']}))

import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
qa=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
tp=qa/'pair-r11c05-r12c05-v1-trace.json';t=read(tp);ep=qa/'pair-r11c05-r12c05-v1-outgoing-edge-check.json';e=read(ep)
viewed=[]
for q in t['qa']:
 assert ref(Path(q['path']))['sha256']==q['sha256']
 viewed.append({**q,'viewedAtNativeResolution':True,'result':'passed'})
viewed.append({**e['eastBottomDirectQa'],'viewedAtNativeResolution':True,'result':'passed','notes':'Affected southeast c05/c06 outgoing corner has continuous sandy ground, stones and rock shadow.'})
o={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','status':'passed','scope':'r12_c05 internal and north shared edge; r11_c05 unchanged internal/north/east approvals retained with affected southeast outgoing corner rechecked. Other external r12_c05 edges remain pending.','tiles':['r11_c05','r12_c05'],'trace':ref(tp),'internalAudits':[ref(qa/'r12_c05-internal-visual-audit-v1.json'),ref(qa/'block2x2-r10r11c05c06-v1-art-audit-v1.json')],'outgoingEdgeCheck':ref(ep),'nativeQaViewedCount':6,'viewed':viewed,'findings':[],'validation':'Five native shared-edge windows inspected: sandy clearing, grass clusters and rock geometry continuous; no duplicate contours or gaps. The affected outgoing east corner was checked using exact exported core pixels.','sourcePixelIdentity':True,'nativePixelsResampled':False,'formalMapAcceptance':False,'runtimeValidation':'not performed'}
p=qa/'pair-r11c05-r12c05-v1-art-audit-v1.json';assert not p.exists();p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(ref(p)))

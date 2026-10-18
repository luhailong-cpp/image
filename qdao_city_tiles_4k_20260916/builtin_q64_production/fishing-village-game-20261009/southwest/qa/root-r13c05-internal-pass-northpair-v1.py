import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
z=Path(__file__).resolve().parent.parent;q=z/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v=read(q/'repair-r13c05-v1-qa.json');assert v['externalContextBordersUnchanged']
assert len(v['changedWindows'])==15 and len(v['reused'])==24
for it in v['changedWindows']+v['reused']+v['local']:assert ref(it['file'])['sha256']==it['sha256']
ap=q/'r13_c05-internal-visual-audit-v1.json'
write(ap,{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','tile':'r13_c05','status':'internal_visual_qa_passed','repairTrace':v['trace'],'candidate':v['candidate'],'context':v['context'],'nativeQaViewedCount':39,'changedQaViewedCount':15,'localRepairPerimetersViewedCount':3,'viewed':[dict(it,result='passed',viewedAtNativeResolution=True) for it in v['changedWindows']+v['local']],'reusedPassedWindows':v['reused'],'baselineAudit':ref(q/'r13_c05-internal-visual-audit-initial-v1.json'),'qaIndex':ref(q/'repair-r13c05-v1-qa.json'),'findings':[],'resolved':['Rock foot and beach rectangle removed with continuous silhouette and shadow.','Ochre shallow-water patch returned to organic pale water transition.','Blue water rectangular tone boundary removed while retaining caustic detail.'],'externalContextBordersUnchanged':True,'externalJoins':'pending','nativePixelsResampled':False,'formalMapAcceptance':False})
idx=read(z/'art-delivery-index.json'); north=next(t for t in idx['artAccepted'] if t['tile']=='r12_c05')
assert north['nativeContext']['sha256']=='553c768b543ceacdc5b4bff31184b0302209d5f114279436d031ee15f46bc671'
mp=q/'r12c05-r13c05-pair-v1-manifest.json'
write(mp,{'outputPrefix':'pair-r12c05-r13c05-v1','inputs':[{'tile':'r12_c05','context':north['nativeContext']},{'tile':'r13_c05','context':v['context']}],'provenance':[north['artAudit'],north['sourceTrace'],v['trace'],ref(ap)]})
subprocess.run([sys.executable,'-B',str(q/'adopt-internal-audit.py'),str(ap)],check=True)
subprocess.run([sys.executable,'-B',str(q/'native-pair-compose.py'),'--manifest',str(mp)],check=True)
print(json.dumps({'internalAudit':ref(ap),'manifest':ref(mp)}))

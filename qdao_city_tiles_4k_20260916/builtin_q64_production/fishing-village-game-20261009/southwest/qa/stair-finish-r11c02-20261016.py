from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def save(p,x):
 assert not p.exists(),p
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=read(Q/'repair-r11_c02-internal-v1-trace.json')
old=read(Q/'r11_c02-internal-native-art-audit-v1.json')
for v in old['viewed']:
 assert ref(Path(v['file']))['sha256']==v['sha256']
for k in ['baseContext','baseCandidate','candidate','context']:
 assert ref(Path(t[k]['path']))['sha256']==t[k]['sha256']
a={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r11_c02','status':'internal_visual_qa_passed','reviewer':'stair_finish_1016','candidate':t['candidate'],'context':t['context'],'trace':ref(Q/'repair-r11_c02-internal-v1-trace.json'),'priorNative39WindowAudit':ref(Q/'r11_c02-internal-native-art-audit-v1.json'),'repairAfterViewed':ref(Q/'repair-r11_c02-internal-v1-lantern-after-100pct.png'),'validation':'Prior 39 native window review reused after checking all hashes. Full 1254px repaired crop reviewed including all local source-selection boundaries: wood bracket fixed to trunk, rope and knot reach lantern ring, lantern position unchanged, no boundary breaks.','issues':[],'externalJoinsVerified':False}
save(Q/'r11_c02-internal-native-art-audit-v2.json',a)
m={'outputPrefix':'pair-r11c02-c03-v1','inputs':[{'tile':'r11_c02','context':t['context']},{'tile':'r11_c03','context':ref(Q/'pair-r10c03-r11c03-v1-r11_c03-context-native.png')}],'provenance':[ref(Q/'r11_c02-internal-native-art-audit-v2.json'),ref(Q/'pair-r10c03-r11c03-v1-trace.json'),ref(Q/'pair-r10c03-r11c03-v1-art-audit-v1.json')]}
save(Q/'pair-r11c02-c03-v1.manifest.json',m)
print(json.dumps({'audit':ref(Q/'r11_c02-internal-native-art-audit-v2.json'),'manifest':ref(Q/'pair-r11c02-c03-v1.manifest.json')}))

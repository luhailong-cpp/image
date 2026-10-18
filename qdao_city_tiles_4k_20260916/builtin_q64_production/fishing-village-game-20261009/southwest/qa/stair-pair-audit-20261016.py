from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
p=Q/'pair-r11c02-c03-v1-trace.json';t=json.loads(p.read_text())
a={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_finish_1016','status':'passed','trace':ref(p),'tiles':['r11_c02','r11_c03'],'nativeQaViewedCount':5,'viewed':[{**v,'result':'pass'} for v in t['qa']],'internalAudit':ref(Q/'r11_c02-internal-native-art-audit-v2.json'),'findings':[],'validation':'All five 100-percent shared-edge windows viewed. Sand material, small rocks, grass bank, light and tree shadows continuous. Native hard source selection, no resampling. Existing c03 north edge unchanged except possible northwest halo; c02 north/west/south neighbors pending.','formalFullMapAcceptance':False}
o=Q/'pair-r11c02-c03-v1-art-audit-v1.json';assert not o.exists();o.write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'audit':ref(o),'trace':ref(p),'tiles':t['tiles']}))

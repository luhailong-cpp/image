import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
tp=Q/'pair-r11c02-r12c02-v1-trace.json';t=read(tp);ep=Q/'pair-r11c02-r12c02-v1-outgoing-edge-check.json';e=read(ep)
viewed=[]
for q in t['qa']:
 assert ref(Path(q['path']))['sha256']==q['sha256']
 viewed.append({**q,'viewedAtNativeResolution':True,'result':'passed'})
viewed.append({**e['eastBottomDirectQa'],'viewedAtNativeResolution':True,'result':'passed','notes':'Affected southeast r11_c02/r11_c03 corner remains continuous across sandy ground and pebble texture.'})
assert e['northContextStripUnchanged'] and e['northEastBeforeBottomOverlapUnchanged'] and e['southBelowTopOverlapUnchanged']
o={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_resume_1017','status':'passed','scope':'r12_c02 internal and north shared edge; r11_c02 prior internal/north/east approval reused where pixels unchanged, affected east outgoing corner rechecked. Other r12_c02 external joins remain pending.','tiles':['r11_c02','r12_c02'],'trace':ref(tp),'internalAudits':[ref(Q/'r12_c02-internal-visual-audit-v1.json'),ref(Q/'pair-r11c02-c03-v1-art-audit-v1.json')],'outgoingEdgeCheck':ref(ep),'nativeQaViewedCount':6,'viewed':viewed,'findings':[],'validation':'All five native shared-edge windows and one affected outgoing corner viewed. Foliage, ground transition and sandy grain remain continuous; no duplicated branches or clipped ground contour observed. North changes limited to context y4115..4325; south changes limited to y0..174, all covered by shared-edge QA.','sourcePixelIdentity':True,'nativePixelsResampled':False,'formalMapAcceptance':False,'runtimeValidation':'not performed'}
ap=Q/'pair-r11c02-r12c02-v1-art-audit-v1.json';write(ap,o)
h={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'worker':'stair_resume_1017','tile':'r12_c02','status':'art_passed_ready_for_root_versioned_export','trace':ref(tp),'artAudit':ref(ap),'internalAudit':ref(Q/'r12_c02-internal-visual-audit-v1.json'),'tiles':t['tiles'],'notes':['Existing 16/16 sources recovered and verified, no repeated image generation.','All 39 internal QA windows and six connection/affected-edge windows actually viewed at original resolution.','New r11_c02 and r12_c02 candidates ready for root versioned export; this worker did not touch index/progress/export/Git.','East r12_c03 external reserved; no unaccepted neighbor source used. Full four-tile corner and other outer joins remain pending available accepted anchors.','r11_c04 prior failed 60px stair-riser issue untouched.']}
hp=Q/'r12_c02-resume-20261017-handoff-v1.json';write(hp,h)
print(json.dumps({'audit':ref(ap),'handoff':ref(hp),'trace':ref(tp),'tiles':t['tiles']}))


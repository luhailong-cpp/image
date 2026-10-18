import sys
sys.dont_write_bytecode=True
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
z=Path(__file__).resolve().parent.parent
qa=z/'qa'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p): return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def write(p,v):
 assert not p.exists(),p
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assembly=qa/'full-tile-r12_c05-assembly.json'; a=read(assembly)
assert ref(a['output']['path'])['sha256']=='ede532bf22f3bc85fa974e230ab6cb666bdcc4a37a11739be4ffd3ecec73525e'
assert len(a['qa'])==39
viewed=[]
for q in a['qa']:
 assert ref(q['file'])['sha256']==q['sha256']
 viewed.append({**q,'viewedAtNativeResolution':True,'result':'passed'})
audit=qa/'r12_c05-internal-visual-audit-v1.json'
write(audit,{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','tile':'r12_c05','status':'internal_visual_qa_passed','trace':ref(assembly),'candidate':a['output'],'context':a['context'],'nativeQaViewedCount':39,'viewed':viewed,'findings':[],'notes':['All 30 native seam segments and nine 900px intersections were visually inspected. First 30 inspected before context handoff, source hash unchanged; final nine inspected after handoff.','Two bamboo net drying racks retain continuous support poles, tied ropes, coherent mesh and shadows across core seams. Rocks and sandy clearing remain continuous.','Lower-right h3072 segment rechecked: foam density varies along the organic wave front, with continuous shoreline and rock geometry; no rectangular break or clipped contour observed.','p04_04_v2 selected; superseded first attempt retained.'],'externalJoins':'pending adjacent contexts and native shared-edge review','nativePixelsResampled':False,'formalMapAcceptance':False,'runtimeValidation':'not performed'})
idx=read(z/'art-delivery-index.json'); north=next(x for x in idx['artAccepted'] if x['tile']=='r11_c05')
assert north['nativeContext']['sha256']=='f5eef04314ed9816a5551565c3987fcab99baa035f5b3ad9e5e78802951be011'
manifest=qa/'r11c05-r12c05-pair-v1-manifest.json'
write(manifest,{'outputPrefix':'pair-r11c05-r12c05-v1','inputs':[{'tile':'r11_c05','context':north['nativeContext']},{'tile':'r12_c05','context':a['context']}],'provenance':[north['artAudit'],north['sourceTrace'],ref(assembly),ref(audit)]})
print(json.dumps({'audit':ref(audit),'manifest':ref(manifest)}))

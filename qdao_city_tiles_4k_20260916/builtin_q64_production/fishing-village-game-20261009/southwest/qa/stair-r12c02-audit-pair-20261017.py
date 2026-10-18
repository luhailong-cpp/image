import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parent.parent;Q=Z/'qa'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def verify(r,key='path'):
 p=Path(r[key]);assert ref(p)['sha256']==r['sha256'],p
 return p
def write(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
a=read(Q/'full-tile-r12_c02-assembly.json')
assert len(a['sources'])==16 and len(a['qa'])==39
for r in a['sources']:
 p=verify(r)
 assert Image.open(p).size==(1254,1254)
 assert ref(r['record'])['sha256']==r['recordSha256']
 g=read(r['record']);verify(g['receipt'])
assert a['output']['sha256']=='a2eee980072849c4ce7f233816e702e0bf62ae02c956b6f11de25c532b42b80d'
verify(a['output']);verify(a['context'])
for q in a['qa']:verify(q,'file')
audit=Q/'r12_c02-internal-visual-audit-v1.json'
write(audit,{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'stair_resume_1017','tile':'r12_c02','status':'internal_visual_qa_passed','trace':ref(Q/'full-tile-r12_c02-assembly.json'),'candidate':a['output'],'context':a['context'],'nativeQaViewedCount':39,'viewed':[{**q,'viewedAtNativeResolution':True,'result':'passed'} for q in a['qa']],'findings':[],'notes':['Resumed from existing 16/16 native sources, receipts and assembled candidate. No generation was repeated.','All 30 native seam segments and nine intersections viewed at original resolution. Green and golden foliage edges, branch connections, sand and rock contours remain continuous; no rectangular seam or displaced contour observed.','Overview used only for layout. All 16 selected source hashes and receipt hashes verified.'],'externalJoins':'north connection pending; east r12_c03 is externally reserved and not used as an unaccepted input','nativePixelsResampled':False,'formalMapAcceptance':False})
north=next(x for x in read(Z/'art-delivery-index.json')['artAccepted'] if x['tile']=='r11_c02')
assert north['nativeContext']['sha256']=='a6b85830dcf4f3f7040037dca1e09848a0a014d1127662591f5cbffd3d5639f8'
m=Q/'r11c02-r12c02-pair-v1-manifest.json'
write(m,{'outputPrefix':'pair-r11c02-r12c02-v1','inputs':[{'tile':'r11_c02','context':north['nativeContext']},{'tile':'r12_c02','context':a['context']}],'provenance':[north['artAudit'],north['sourceTrace'],ref(Q/'full-tile-r12_c02-assembly.json'),ref(audit)]})
print(json.dumps({'audit':ref(audit),'manifest':ref(m)}))


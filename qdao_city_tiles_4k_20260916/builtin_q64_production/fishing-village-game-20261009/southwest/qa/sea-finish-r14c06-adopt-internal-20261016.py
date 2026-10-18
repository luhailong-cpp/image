import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent.parent; Q=Z/'qa'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mp=Q/'full-tile-r14_c06-assembly.json';d=read(mp)
assert len(d['qa'])==39
for r in d['sources']:assert sha(r['path'])==r['sha256']
for r in d['qa']:assert sha(r['file'])==r['sha256']
a={'schemaVersion':1,'tile':'r14_c06','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'internal_visual_qa_passed','selectedUniqueCoreCount':16,'nativeCoreSize':1024,'nativeSourceDimensions':[1254,1254],'candidate':d['output'],'context':d['context'],'trace':ref(mp),'baseAssembly':ref(mp),'nativeInternalChecks':[{'file':r['file'],'inputSha256':r['sha256'],'sourceBox':r['sourceBox'],'viewedAtNativeResolution':True,'status':'passed','notes':'Rock silhouettes and surface facets, foam contours, water rhythm and foliage connections visually continuous; no rectangular source boundary, cut object, gap or black edge.'} for r in d['qa']],'compositionPreview':{**ref(Q/'r14_c06-composition-preview-v1.png'),'previewOnly':True,'nativeAcceptanceEvidence':False,'operation':'4096 to 1254 reduction for composition only'},'sourcePixelIdentity':True,'nativePixelsResampled':False,'checksReused':False,'externalJoins':'r14_c07 join next; north and west pending neighboring tile availability','runtimeValidation':'not performed','formalMapAcceptance':False,'unresolvedInternalIssues':[]}
ap=Q/'r14_c06-internal-visual-audit-v1.json';write(ap,a)
e=read(Q/'r14_c07-internal-visual-audit-v2.json')
assert sha(e['context']['path'])==e['context']['sha256']
manifest={'outputPrefix':'pair-r14c06-r14c07-v1','inputs':[{'tile':'r14_c06','context':d['context']},{'tile':'r14_c07','context':e['context']}],'provenance':[ref(ap),ref(mp),ref(Q/'r14_c07-internal-visual-audit-v2.json'),e['repairTrace']]}
pm=Q/'pair-r14c06-r14c07-v1.manifest.json';write(pm,manifest)
write(Q/'r14_c06-composition-preview-v1.png.derivation.json',{'file':ref(Q/'r14_c06-composition-preview-v1.png'),'source':d['output'],'operation':'LANCZOS downsample for composition inspection only','notNativeAcceptanceEvidence':True})
print(json.dumps({'audit':ref(ap),'candidate':d['output'],'manifest':ref(pm)}))


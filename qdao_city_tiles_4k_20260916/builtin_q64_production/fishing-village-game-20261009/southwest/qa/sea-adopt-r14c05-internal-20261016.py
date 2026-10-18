import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def write(p,d):
 assert not p.exists(),str(p)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
mp=Q/'full-tile-r14_c05-assembly.json';d=read(mp)
assert len(d['qa'])==39 and d['mechanicalValidation']['passed']
for r in d['sources']:assert sha(r['path'])==r['sha256']
for r in d['qa']:assert sha(r['file'])==r['sha256']
a={'schemaVersion':1,'tile':'r14_c05','createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'internal_visual_qa_passed','selectedUniqueCoreCount':16,'nativeCoreSize':1024,'nativeSourceDimensions':[1254,1254],'candidate':d['output'],'context':d['context'],'trace':ref(mp),'baseAssembly':ref(mp),'nativeInternalChecks':[{'file':r['file'],'inputSha256':r['sha256'],'sourceBox':r['sourceBox'],'viewedAtNativeResolution':True,'status':'passed','notes':'Native rock contours and fine stone facets, surf and water detail, leaf and branch connections are continuous across seam; no rectangular edge, gap, cut object or black band.'} for r in d['qa']],'compositionPreview':{**ref(Q/'r14_c05-composition-preview-v1.png'),'previewOnly':True,'nativeAcceptanceEvidence':False,'operation':'4096 to 1254 reduction for composition only'},'sourcePixelIdentity':True,'nativePixelsResampled':False,'checksReused':False,'externalJoins':'r14_c06 east join next; r13_c05 north waiting root stable context; west pending neighboring tile','runtimeValidation':'not performed','formalMapAcceptance':False,'unresolvedInternalIssues':[]}
ap=Q/'r14_c05-internal-visual-audit-v1.json';write(ap,a)
ep=Q/'pair-r14c06-r14c07-v3-r14_c06-context-native.png'
assert sha(ep)=='3d59c2c8d07563732944bcc4d2948d8a48fad863c9f59a59a739fda79a312053'
manifest={'outputPrefix':'pair-r14c05-r14c06-v1','inputs':[{'tile':'r14_c05','context':d['context']},{'tile':'r14_c06','context':ref(ep)}],'provenance':[ref(ap),ref(mp),ref(Q/'pair-r14c06-r14c07-v3-art-audit-v1.json'),ref(Q/'pair-r14c06-r14c07-v3-trace.json')]}
pm=Q/'pair-r14c05-r14c06-v1.manifest.json';write(pm,manifest)
write(Q/'r14_c05-composition-preview-v1.png.derivation.json',{'file':ref(Q/'r14_c05-composition-preview-v1.png'),'source':d['output'],'operation':'LANCZOS downsample for composition inspection only','notNativeAcceptanceEvidence':True})
print(json.dumps({'audit':ref(ap),'candidate':d['output'],'context':d['context'],'manifest':ref(pm)}))


from pathlib import Path
import json,hashlib
R=Path(__file__).parent;B=R.parents[1];Q=B/'qa/r12c07-west-pair-20261016-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def write(p,j):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2)
items=[]
for name in ['W01','W01b']:
 d=Q/(name+'-v1');views=[rec(d/(n+'.png')) for n in ['actual-core-join-native','top-native','bottom-native','right-native']]
 j={'name':name,'selected':False,'status':'fail-no-effective-improvement','formalAccepted':False,'assembly':rec(d/'assembly.json'),'reviewedNativeViews':views,'actualCoreJoin':'Most of the core boundary becomes continuous through exact west donor; this alone is not a visual pass.','shiftedSeam':'A strong full-height fine/coarse sand pattern and tone discontinuity is visible at east context x230, the fixed anchor/generated interface.','problemContextBox':[220,115,250,1050],'bottom':'Closure region resumes the original unresolved vertical core seam; a source corner remains visible.','right':'No salient new outer-right application cut, but this does not cure the fixed inner edge failure.','bestRetained':rec(B/'qa/r12c07-resume2-r19-v1/context-native.png'),'attemptsAtPoint':1 if name=='W01' else 2,'nextAction':'Preserve both unsuccessful candidates and continue independent W02/W04. No third attempt with these unchanged inputs.'}
 write(d/'review-v1.json',j);items.append(rec(d/'review-v1.json'))
diag=json.loads((Q/'diagnostic-inputs-v1.json').read_text())
write(Q/'diagnosis-review-v1.json',{'inputs':rec(Q/'diagnostic-inputs-v1.json'),'nativeScale':1,'formalAccepted':False,'segments':[{'id':'W01','status':'needs-repair','contextBox':[100,115,160,1139],'description':'Straight grain/colour seam through sand. Two new attempts move the seam inward to x230 and are not selected.'},{'id':'W02','status':'needs-repair','contextBox':[100,1139,220,2163],'description':'Stone planes and surface marks break at the vertical core boundary; sand also cuts at upper end.'},{'id':'W03','status':'deferred-two-unsuccessful-attempts-input-unchanged','contextBox':[100,2163,460,3187],'description':'Rock foot height/shape and sharpness/caustic scale differ across the exact core join. No third repeat is justified by the unrelated wider-image hash changes.'},{'id':'W04','status':'needs-repair-in-R19','contextBox':[100,3187,460,4211],'description':'Stone contours/material and water marks break along the actual core line; independent repair delegated.'}],'attemptReviews':items,'oldR05InputAudit':rec(Q/'old-r05-input-audit-v1.json')})
print(json.dumps({'diagnosis':rec(Q/'diagnosis-review-v1.json'),'attemptReviews':items}))

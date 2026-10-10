from pathlib import Path
import assembly_r07_c16 as a
R=Path(__file__).resolve().parent;T=R/'r07_c16';D=T/'repairs/west-upper-three';OLD=T/'repairs/west-upper-integrated';Q=D/'qa'
def ref(p):return dict(file=str(p),sha256=a.sha(p))
assert a.sha(D/'candidate.png')=='4104373b3faa477b95d4ec6b9df3cf29a25e49d8593d6def8ad60c123957830f'
items=[]
for name in ['upper-left-join','timber-underside','upper-overlap','post-waterline']:
 p=Q/(name+'.png');prior=OLD/'qa'/(name+'.png');items.append(dict(ref(p),actualView=True,priorVersion=ref(prior),sameShaAsPrior=a.sha(p)==a.sha(prior),result='pass-upper-west-insertion-scope'))
for name in ['bottom-insertion','east-insertion-full','west-common-full']:
 items.append(dict(ref(Q/(name+'.png')),actualView=True,result='pass-y0..3236-scope-only',observation='Upper timber rail and post joins connect; quiet broad reflected water has no straight color cut. Lower western joint remains pending stable c15.'))
natives=[]
for i in [1,2,3]:
 p=T/'repairs/west-only-joint'/f's{i}.png';natives.append(dict(ref(p),record=ref(Path(str(p)+'.generation.json')),actualView=True,result='selected-for-upper-scope-integration',actualModel=None,actualQuality=None))
H=T/'repairs/integrated-southwest-v3/qa/assembly';internal=[]
for y in [1024,2048,3072]:internal.append(dict(ref(H/f'internal-horizontal-y{y}-full.png'),actualView=True,result='pass-internal-horizontal-scope'))
a.save_json(D/'local-review.json',dict(createdAtUtc=a.utc_now(),reviewer='close_joint14',candidate=ref(D/'candidate.png'),result='pass-upper-west-through-y3236-pending-final-source-validation',items=items,nativeReview=natives,changedInternalHorizontalReview=internal,formalWestBound=False,finalWest627SourceROIValidationRequired=True,formalAccepted=False))
print(a.sha(D/'local-review.json'))

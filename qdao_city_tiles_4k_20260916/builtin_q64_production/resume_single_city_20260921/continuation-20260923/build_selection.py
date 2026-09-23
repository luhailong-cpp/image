from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent.parent
A=S.parent.parent
def ref(p):return {'file':p.relative_to(A).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
candidates=[];local=[]
ledger=json.loads((S/'current-coverage-ledger.json').read_text(encoding='utf-8-sig'))
current={x['tile']:x['candidate'] for x in ledger['tiles'] if x['candidateExists']}
for tid in ('r08_c07','r08_c09'):
    pointer=S/f'next_tile_{tid}/latest-candidate.json'
    d=json.loads(pointer.read_text())
    candidates.append({**d['candidate'],'tile':tid,'status':d['status'],'record':d['record'],'qa':d['review'],'assembly':d['assembly'],'selection':ref(pointer),'scopedLocalContinuityPassed':False,'actualModel':None,'actualQuality':None,'backendModelVerified':False})
    neighbor=tid.replace('r08','r09')
    local.append({'id':f'{tid}|{neighbor}','candidateSha256ByTile':{tid:d['candidate']['sha256'],neighbor:current[neighbor]['sha256']},'result':'passed' if tid=='r08_c07' else 'failed','evidence':d['review']})
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
selection={'schemaVersion':1,'selectedCandidates':candidates,'localReviews':local,'modelCapabilityEvidence':ref(S/'continuation-20260923/model-capability.json'),'retentionEvidence':[ref(S/'next_tile_r08_c07/continuation-20260923/cleanup-selected-c07/receipt.json')],'additionalNativeSources':[]}
p=S/'continuation-20260923/checkpoint-merge'/f'selected-{stamp}.json'
with p.open('x',encoding='utf-8') as f:json.dump(selection,f,ensure_ascii=False,indent=2);f.write('\n')
print(str(p))

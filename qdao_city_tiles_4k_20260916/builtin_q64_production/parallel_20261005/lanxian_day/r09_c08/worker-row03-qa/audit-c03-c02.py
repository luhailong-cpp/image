from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day')/'r09_c08'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=[]
for cell in ['r03_c03','r03_c02']:
 p=R/'native'/(cell+'.png');g=Path(str(p)+'.generation.json');d=json.loads(g.read_text(encoding='utf-8-sig'))
 checks=[{'role':'native','file':str(p),'expected':d['sha256'],'actual':sha(p)},{'role':'sourceOutput','file':d['evidence']['sourceOutputPath'],'expected':d['evidence']['sourceOutputSha256'],'actual':sha(d['evidence']['sourceOutputPath'])},{'role':'receipt','file':d['evidence']['toolResultPath'],'expected':d['evidence']['toolResultSha256'],'actual':sha(d['evidence']['toolResultPath'])},{'role':'prompt','file':d['prompt'],'expected':d['promptSha256'],'actual':sha(d['prompt'])},{'role':'job','file':d['sourceJob'],'expected':d['sourceJobSha256'],'actual':sha(d['sourceJob'])}]
 for ref in d['references']:checks.append({'role':ref['role'],'file':ref['path'],'expected':ref['sha256'],'actual':sha(ref['path'])})
 assert all(q['expected']==q['actual'] for q in checks)
 assert d['actualModel'] is None and d['actualQuality'] is None and d['submittedParameters']['model'] is None and d['submittedParameters']['quality'] is None
 out.append({'cell':cell,'generationRecord':str(g),'generationSha256':sha(g),'hashChecksPassed':True,'undisclosedSelectorsNotMisrepresented':True,'checks':checks})
audit={'createdAt':datetime.now(timezone.utc).isoformat(),'scope':'row3 own completed cells only','results':out,'nativeOrEvidenceModified':False,'formalAcceptance':False}
dest=R/'worker-row03-qa'/'records-audit-c03-c02.json';assert not dest.exists();dest.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'audit':str(dest),'auditSha256':sha(dest),'allChecksPassed':True}))


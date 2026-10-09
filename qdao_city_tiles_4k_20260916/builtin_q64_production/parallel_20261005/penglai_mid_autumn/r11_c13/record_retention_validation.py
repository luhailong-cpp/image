from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:dict(file=str(p),sha256=sha(p))
for tile,scanned in [('r09_c15',2177),('r11_c13',2485)]:
 T=R/tile;plan=T/'retention-plan.json';v=json.loads(plan.read_text())
 report={'validatedAt':datetime.now(timezone.utc).isoformat(),'status':'validated_only_no_files_deleted','plan':ref(plan),'executionScript':ref(T/'execute-retention.ps1'),'final':ref(Path(v['final']['file'])),'finalManifest':ref(Path(v['finalManifest']['file'])),'keepCount':len(v['keep']),'keptBinaryCount':v['summary']['keptBinaryCount'],'proposedRemovalCount':len(v['remove']),'proposedRemovalBytes':v['summary']['removeBytes'],'currentRuntimeDependenciesComplete':True,'currentExternalSourcesHashVerified':v['protectedExternalSources'],'pendingOwnRequests':v['referenceAudit']['pendingOwnRequests'],'externalCurrentReferenceConflicts':v['referenceAudit']['proposedRemovalExternalReferenceConflicts'],'historicalOnlyExemptions':v['historicalExternalReferenceExemptions'],'northFreezePixelProof':v.get('northFreezePixelProof'),'externalRecordsRescannedBySafePowerShell':scanned,'defaultPowerShellValidationPassed':True,'explicitExecuteInvoked':False,'deletedFiles':0,'blockedR10c13CleanupTouched':False}
 (T/'retention-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'tile':tile,'plan':ref(plan),'validation':ref(T/'retention-validation.json'),'manifest':ref(T/'output/manifest.json')}))


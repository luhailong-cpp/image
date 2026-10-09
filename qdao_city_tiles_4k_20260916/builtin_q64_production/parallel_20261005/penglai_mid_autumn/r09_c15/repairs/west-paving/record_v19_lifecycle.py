from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
P=Path(__file__).parent;T=P.parent.parent;H=P/'history-before-v19-application'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:dict(file=str(p),sha256=sha(p))
records=[]
# Preserve historical references as past facts and explicitly resolve their lifecycle.
for old in H.rglob('*.png.generation.json'):
 v=json.loads(old.read_text(encoding='utf-8-sig'));f=v.get('file');h=v.get('sha256')
 if not f or not h:continue
 current=Path(f);same=current.exists() and sha(current)==h
 records.append({'historicalImageFile':f,'historicalImageSha256':h,'historicalGeneration':ref(old),'historicalPixelsStillAvailableAtOriginalPath':same,'currentFile':ref(current) if current.exists() else None,'lifecycle':'identical_pixels_remain_current' if same else 'supersededAfterApprovedRepair_no_PNG_backup','historicalRecordWasNotRewritten':True})
v={'recordedAt':datetime.now(timezone.utc).isoformat(),'application':ref(P/'application-v19.json'),'immutableNativeAssembly':ref(T/'output/native-assembly.json'),'immutableAssemblyCandidateSha256':'957194bcbf888cac88f8b0a3d79d055f8ce69a76846590f174eee7e6f8b9e456','currentCandidate':ref(T/'output/r09_c15-candidate.png'),'records':records,'policy':'Historical image/hash references describe pixels before approved application. Changed old PNGs have no backup and are not claimed to exist. All original source AI images remain while this tile is pending finalization.','currentRuntimeReferencesUseNewCandidate':True,'downstreamActivePlanOrRequestOldCandidateHashMatches':0}
q=P/'source-lifecycle-v19.json';q.write_text(json.dumps(v,indent=2)+'\n')
m=T/'output/manifest.json';data=json.loads(m.read_text());data['sourceLifecycleRecord']=ref(q);m.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'historicalImages':len(records),'changedRetired':sum(not r['historicalPixelsStillAvailableAtOriginalPath'] for r in records),'lifecycle':ref(q)}))


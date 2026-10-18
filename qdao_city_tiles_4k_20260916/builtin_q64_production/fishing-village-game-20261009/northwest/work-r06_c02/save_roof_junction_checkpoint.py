from pathlib import Path
import json
from datetime import datetime,timezone
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r06_c02'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=rd(W/'joint-v2/assembly.json');now=datetime.now(timezone.utc).isoformat()
record={'updatedAt':now,'tile':'r06_c02','selectedCoreCount':16,'candidate':a['candidate'],'assembly':'work-r06_c02/joint-v2/assembly.json','qa':'work-r06_c02/joint-v2/local-qa.json','internalAccepted':False,'formalAccepted':False,'resolvedThisBatch':['four-core roof junction tile discontinuity','horizontal seam under roof junction','lower-right patch notch'],'pending':['top ridge and tile join still fails on returned repair east/south boundaries','ground transition and complete tile QA still pending'],'lastRejectedRepair':'native/r06_c02_roof_top_v01.png','inFlightGeneration':False,'actualModel':None,'runtime':{'rootImagegen':'successful','sol_e3':'HTTP408 request body read timed out'}}
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
wr(B/'production-checkpoints'/(stamp+'-roof-junction.json'),record)
p=rd(B/'progress.json');p.update(updatedAt=now,status='native-production-candidate-pending-repair',currentTile='r06_c02',currentPatch='joint-v2-local-roof-junction-passed-top-ridge-pending',lastNewOutput=str(B/'native/r06_c02_roof_top_v01.png'),inFlightGeneration=False,currentCheckpoint='production-checkpoints/'+stamp+'-roof-junction.json')
p['currentCandidates']['r06_c02']={'candidate':'work-r06_c02/joint-v2/r06_c02.candidate.png','candidateSha256':a['candidate']['sha256'],'assembly':record['assembly'],'qa':record['qa'],'internalAccepted':False,'formalAccepted':False}
wr(B/'progress.json',p);print(json.dumps(record))

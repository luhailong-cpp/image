from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northwest');W=B/'work-r06_c02'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
a=rd(W/'ground-v1/assembly.json');now=datetime.now(timezone.utc).isoformat()
qa={'reviewedAt':now,'localGroundTransition':'passed','reviewedEdges':['n-1','n-2','w-1','w-2','e-1','e-2','s-1','s-2'],'nativeSourceSha256':'f8f9c4b56fad9a284659a30627939cadfc8954f160c78cc924383f5d08ef1e46','candidate':a['candidate'],'pixelReplayMismatches':0,'wholeTileAccepted':False,'pending':['upper roof ridge join','remaining complete tile seam review'],'actualModel':None}
wr(W/'ground-v1/local-qa.json',qa)
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
checkpoint='production-checkpoints/'+stamp+'-ground-joint.json'
wr(B/checkpoint,qa)
p=rd(B/'progress.json');p.update(updatedAt=now,currentTile='r06_c02',currentPatch='ground-v1-local-passed-roof-ridge-pending',lastNewOutput=str(B/'native/r06_c02_ground_joint_v01.png'),inFlightGeneration=False,currentCheckpoint=checkpoint)
p['currentCandidates']['r06_c02']={'candidate':'work-r06_c02/ground-v1/r06_c02.candidate.png','candidateSha256':a['candidate']['sha256'],'assembly':'work-r06_c02/ground-v1/assembly.json','qa':'work-r06_c02/ground-v1/local-qa.json','internalAccepted':False,'formalAccepted':False}
wr(B/'progress.json',p)
print(checkpoint)


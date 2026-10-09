from pathlib import Path
import json,hashlib
D=Path(__file__).parent;O=D/'join-v1';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=read(D/'repair-proof.json');p['operation']='True AI native repair crops with 8pixel texture edge transitions and40pixel vertical-joint end transitions; no blur, resize, warp or tone correction.';save(D/'repair-proof.json',p)
g=read(D/'native-repaired.png.generation.json');g['repairProof']=ref(D/'repair-proof.json');save(D/'native-repaired.png.generation.json',g)
g.update(file=str(D/'native.png'),sha256=sha(D/'native.png'),derivedFrom=[ref(D/'native-repaired.png')],operation='Lossless copy of explicitly composited native AI repairs; this file is not an unmodified tool output',newModelCalls=0);save(D/'native.png.generation.json',g)
save(D/'tool-receipt.json',{'operation':'Final native.png is an explicit composition. Actual tool outputs and requests are recorded separately.','actualToolOutputRecords':[ref(D/(f+'.generation.json')) for f in ['native-original.png','repair-1-native.png','repair-2-native.png']],'nativeComposition':ref(D/'repair-proof.json'),'actualModel':None,'actualQuality':None})
a=read(O/'assembly.json');a['nativeRepairEvidence']=ref(D/'repair-proof.json');save(O/'assembly.json',a)
g=read(O/'joined.png.generation.json');g['assembly']=ref(O/'assembly.json');save(O/'joined.png.generation.json',g)

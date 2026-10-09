from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
N=Path(__file__).resolve().parent;T=N.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (N/'local-source-checkpoint.json').exists(),'Never reseed an existing local chain'
raw=(T/'source-checkpoint.json').read_bytes();cp=json.loads(raw.decode('utf-8-sig'))
assert cp['fragment']['tile']=='r08_c12','Root must select the new tile first'
S={v['tile']:v for v in cp['candidateSet']}
for tile in ['r07_c11','r07_c12','r08_c11']:
 v=S[tile];assert sha(v['file'])==v['sha256'];a=np.array(Image.open(v['file']).convert('RGBA'));assert a.shape==(4096,4096,4) and np.all(a[:,:,3]==255)
src=cp['fragment'];assert sha(src['file'])==src['sha256'];assert not np.any(np.array(Image.open(src['file']).convert('RGBA'))[:,:,3])
(N/'root-checkpoint-at-seed.json').write_bytes(raw)
save(N/'initial-neighbor-sources.json',{'sourceCheckpoint':ref(N/'root-checkpoint-at-seed.json'),'sources':{k:S[k] for k in ['r07_c11','r07_c12','r08_c11']},'nativeScale':1,'rootStateModified':False})
save(N/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c12','fragment':src,'coveragePixels':0,'manifest':None,'manifestChain':[],'candidateSet':cp['candidateSet'],'rootSeed':ref(N/'root-checkpoint-at-seed.json'),'rootPublished':False,'formalAccepted':False})
print(json.dumps({'checkpoint':ref(N/'local-source-checkpoint.json'),'rootSeed':ref(N/'root-checkpoint-at-seed.json')}))

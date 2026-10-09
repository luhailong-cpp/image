from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,numpy as np
N=Path(__file__).resolve().parent;T=N.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not (N/'local-source-checkpoint.json').exists()
raw=(T/'source-checkpoint.json').read_bytes();cp=json.loads(raw.decode('utf-8-sig'))
def source(tile):
 m=[v for v in cp['candidateSet'] if v['tile']==tile];assert len(m)==1;s=m[0];assert sha(s['file'])==s['sha256'];return s
left=source('r07_c11');belowleft=source('r08_c11');L=Image.open(left['file']).convert('RGBA');B=Image.open(belowleft['file']).convert('RGBA');assert L.size==B.size==(4096,4096)
assert np.all(np.asarray(L)[:,:,3]==255);assert np.all(np.asarray(B)[:115,3981:,3]==255),'Need real r08_c11 northeast115square after fourth top patch'
(N/'root-checkpoint-at-seed.json').write_bytes(raw);save(N/'initial-neighbor-sources.json',{'sourceCheckpoint':ref(N/'root-checkpoint-at-seed.json'),'sources':{'r07_c11':left,'r08_c11':belowleft},'nativeScale':1,'rootStateModified':False})
p=N/'initial-empty-fragment.png';Image.new('RGBA',(4096,4096),(0,0,0,0)).save(p);src={**ref(p),'tile':'r07_c12','pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'partialFragment':True,'fullyPainted':False,'nativeScale':1,'formalAccepted':False,'generationRecord':str(p)+'.generation.json'}
save(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':src['sha256'],'operation':'Empty transparent native canvas with zero painted pixels; no generated art yet.','nativeScale':1,'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False})
save(N/'local-source-checkpoint.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c12','fragment':src,'coveragePixels':0,'contextJoined':None,'manifest':None,'manifestChain':[],'externalReturnDependencies':[],'contextNeighbors':[],'externalImportEvidence':[],'rootPublished':False,'formalAccepted':False})
print(json.dumps({'left':left,'belowLeft':belowleft,'seed':ref(N/'local-source-checkpoint.json'),'coveragePixels':0}))

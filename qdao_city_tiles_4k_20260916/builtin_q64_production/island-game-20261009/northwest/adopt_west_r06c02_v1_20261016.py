from pathlib import Path
import json,hashlib
Z=Path(__file__).resolve().parent
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
s=Z/'west-current-selection-20261012.json';d=json.loads(s.read_text(encoding='utf8'));assert any(x['tileId']=='r05_c02' and x['internalClosurePassed'] for x in d['completedTiles'])
image=Z/'tiles/r06_c02_candidate-v1_4096.png';record=image.with_suffix('.assembly.json');qa=Z/'qa/assembly_r06_c02_candidate-v1_4096/qa_index.json'
d['currentTile']={'tileId':'r06_c02','candidate':info(image),'record':info(record),'qaIndex':info(qa),'internalClosurePassed':False,'formalAccepted':False,'status':'full_native_candidate_pending33_QA'}
s.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
print(json.dumps(d['currentTile']))


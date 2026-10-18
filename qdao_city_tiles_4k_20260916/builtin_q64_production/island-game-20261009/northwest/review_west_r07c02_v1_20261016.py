from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
q=Z/'qa/assembly_r07_c02_candidate-v1_4096/qa_index.json';index=json.loads(q.read_text());notes=json.loads((Z/'qa/r07_c02_v1_owner_observation_notes_20261016.json').read_text())
assert len(notes)==len(index['seamAndJunctionCrops'])==33
items=[]
for i,x in enumerate(index['seamAndJunctionCrops']):
 assert info(Path(x['path']))['sha256']==x['sha256'];items.append({**x,'status':notes[str(i)][0],'note':notes[str(i)][1],'method':'view_image original, complete crop actually inspected'})
d={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'candidate':info(Z/'tiles/r07_c02_candidate-v1_4096.png'),'record':info(Z/'tiles/r07_c02_candidate-v1_4096.assembly.json'),'qaIndex':info(q),'scope':'Full owner native 33 geometry review. Preview used only for layout, never native evidence.','items':items,'passed':sum(x['status']=='PASS' for x in items),'repair':sum(x['status']=='REPAIR' for x in items),'distinctGeometricIssues':[{'tilePoint':[3072,1040],'issue':'Short step/doubled lower ridge at red wall beam join','status':'PENDING_REPAIR'}],'materialPending':['Foreground yellow flower/leaf and stone post softness, especially bottom row subcolumns1-2.','Dense fragmented stone brush texture on head/body and patterned bark texture, retained pending material review.'],'materialStatus':'PENDING','internalGeometryClosurePassed':False,'internalClosurePassed':False,'formalAccepted':False}
p=Z/'qa/r07_c02_v1_owner_native33_review_20261016.json';assert not p.exists();p.write_text(json.dumps(d,indent=2)+'\n')
s=Z/'west-current-selection-20261012.json';sel=json.loads(s.read_text());sel['currentTile'].update(internalReview=info(p),status='owner_native33_28_geometry_PASS_5_affected_windows_one_repair_pending',materialStatus='PENDING',materialPending=d['materialPending']);s.write_text(json.dumps(sel,indent=2)+'\n')
print(json.dumps({'ownerReview':info(p),'passed':d['passed'],'repair':d['repair']}))

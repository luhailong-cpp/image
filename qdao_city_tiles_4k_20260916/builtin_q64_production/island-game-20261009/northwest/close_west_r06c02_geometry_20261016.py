from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def info(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def verify(p):assert info(p['path'])['sha256']==p['sha256']
s=Z/'west-current-selection-20261012.json';d=read(s);c=d['currentTile'];assert c['tileId']=='r06_c02'
ip=Z/'qa/r06_c02_v2_independent_native33_connected_20261016.json';ind=read(ip);assert info(ip)['sha256']=='2c3f94957b9089deb5ac79af21f5b839e949bd78889401a75a3052339616ec59'
assert ind['geometryPassed']==33 and ind['internalGeometryClosurePassed'] and not ind['internalClosurePassed'] and ind['materialStatus']=='PENDING'
for k in ['candidate','record','qaIndex']:assert c[k]==ind[k];verify(c[k])
owner=read(c['internalReview']['path']);verify(c['internalReview']);verify(c['strictReplay']);assert owner['passed']==33 and read(c['strictReplay']['path'])['all16777216PixelsReplayed']
q=read(c['qaIndex']['path'])
for x in q['seamAndJunctionCrops']:verify(x)
op=Z/'qa/r06_c02_v2_owner_native33_geometry_scope_20261016.json'
owner.update(internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',scope='Internal native geometry only. Full material/artwork and external edges pending.',priorOwnerReview=c['internalReview'],independentReview=info(ip),status='internal_geometry33_PASS_material_and_external_pending')
assert not op.exists();op.write_text(json.dumps(owner,indent=2)+'\n')
closure={'schemaVersion':1,'closedAtUtc':datetime.now(timezone.utc).isoformat(),'tileId':'r06_c02',**{k:c[k] for k in ['candidate','record','qaIndex','strictReplay']},'ownerReview':info(op),'independentReview':info(ip),'geometryPassed':33,'verifiedPixelCount':16777216,'internalGeometryClosurePassed':True,'internalClosurePassed':False,'materialStatus':'PENDING','materialIssues':c['materialPending'],'formalAccepted':False,'externalEdgesStatus':'PENDING'}
out=Z/'qa/r06_c02_v2_geometry_closure_material_pending_20261016.json';assert not out.exists();out.write_text(json.dumps(closure,indent=2)+'\n')
c.update(internalReview=info(op),independentReview=info(ip),closure=info(out),internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',status='internal_geometry33_PASS_material_and_external_pending')
d.setdefault('geometryClosedTiles',[]).append(dict(c))
p=next(x for x in d['partialTiles'] if x['tileId']=='r06_c02');p.update(status='16of16_native_geometry_closed_material_external_pending',internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',geometryClosure=info(out))
s.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'closure':info(out),'ownerReview':info(op)}))


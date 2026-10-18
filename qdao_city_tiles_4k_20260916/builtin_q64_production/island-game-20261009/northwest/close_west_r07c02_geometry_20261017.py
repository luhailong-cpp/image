from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def info(p):return {'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def verify(p):assert info(p['path'])['sha256']==p['sha256'],p
s=Z/'west-current-selection-20261012.json';d=read(s);c=d['currentTile'];assert c['tileId']=='r07_c02'
files=[('qa/r07_c02_v1_first6_independent_connected_20261016_v2.json','91fb9cba4f7d735697c107827e877ae00fcea7abe51c7eff26f7bfa2c96c0656'),('qa/r07_c02_v1_remaining27_root_independent_20261016.json','af2863f0218729080317fa5de8b7f15d5eaf89a89933a6d548ead9d867ec280a'),('qa/r07_c02_v2_root_independent_delta5_20261016.json','a426d83bd4fb099c641a5f09f575faf00821f6e1b242fbc1eedde7924b23f49a')]
sources=[]
for rel,h in files:
 p=Z/rel;assert info(p)['sha256']==h;sources.append((info(p),read(p)))
for k in ['candidate','record','qaIndex','internalReview','strictReplay']:verify(c[k])
delta=sources[2][1]
for k in ['candidate','record','qaIndex']:assert c[k]==delta[k]
verify(delta['fullRepairCrop']);verify(delta['binaryMask']);assert delta['fullRepairCrop']['geometryStatus']=='PASS'
prior={}
for x in sources[0][1]['crops']:prior[Path(x['path']).name]=(x,x['review']['geometry'],sources[0][0])
for x in sources[1][1]['items']:prior[Path(x['path']).name]=(x,x['geometry'],sources[1][0])
changes={Path(x['path']).name:x for x in delta['changedCropChecks']}
q=read(c['qaIndex']['path']);im=Image.open(c['candidate']['path']).convert('RGB');items=[]
for x in q['seamAndJunctionCrops']:
 verify(x);assert np.array_equal(np.asarray(im.crop(x['tileCropBoxHalfOpen'])),np.asarray(Image.open(x['path']).convert('RGB')))
 name=Path(x['path']).name
 if name in changes:
  x2=changes[name];assert x2['sha256']==x['sha256'] and x2['geometryStatus']=='PASS';source=sources[2][0];method='Actual original-size changed crop independent review'
 else:
  x2,status,source=prior[name];assert status=='PASS' and x2['sha256']==x['sha256'];method='Prior independent PASS reused after exact pixel identity check against current v2 candidate'
 items.append({**x,'geometry':'PASS','reviewSource':source,'method':method})
assert len(items)==33 and len(changes)==5
owner=read(c['internalReview']['path']);assert owner['passed']==33 and all(x['status']=='PASS' for x in owner['items']);strict=read(c['strictReplay']['path']);assert strict['all16777216PixelsReplayed'] and strict['proof']['verifiedPixelCount']==16777216
ip=Z/'qa/r07_c02_v2_independent_native33_combined_20261017.json';assert not ip.exists()
ind={'createdAtUtc':datetime.now(timezone.utc).isoformat(),**{k:c[k] for k in ['candidate','record','qaIndex']},'items':items,'sourceRecords':[x[0] for x in sources],'fullRepairCrop':delta['fullRepairCrop'],'binaryMask':delta['binaryMask'],'geometryPassed':33,'internalGeometryClosurePassed':True,'internalClosurePassed':False,'materialStatus':'PENDING','formalAccepted':False}
ip.write_text(json.dumps(ind,indent=2)+'\n')
op=Z/'qa/r07_c02_v2_owner_native33_geometry_scope_20261017.json';assert not op.exists()
owner.update(internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',scope='Internal native geometry only. Material/artwork and external edges remain pending.',priorOwnerReview=c['internalReview'],independentReview=info(ip),status='internal_geometry33_PASS_material_and_external_pending')
owner['distinctGeometricIssues'][0]['status']='RESOLVED_GEOMETRY_IN_V2_OWNER_AND_INDEPENDENT_PASS'
op.write_text(json.dumps(owner,indent=2)+'\n')
closure={'schemaVersion':1,'closedAtUtc':datetime.now(timezone.utc).isoformat(),'tileId':'r07_c02',**{k:c[k] for k in ['candidate','record','qaIndex','strictReplay']},'ownerReview':info(op),'independentReview':info(ip),'geometryPassed':33,'verifiedPixelCount':16777216,'internalGeometryClosurePassed':True,'internalClosurePassed':False,'materialStatus':'PENDING','materialIssues':c['materialPending'],'formalAccepted':False,'externalEdgesStatus':'PENDING'}
out=Z/'qa/r07_c02_v2_geometry_closure_material_pending_20261017.json';assert not out.exists();out.write_text(json.dumps(closure,indent=2)+'\n')
c.update(internalReview=info(op),independentReview=info(ip),closure=info(out),internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',status='internal_geometry33_PASS_material_and_external_pending')
assert not any(x['tileId']=='r07_c02' for x in d.get('geometryClosedTiles',[]));d.setdefault('geometryClosedTiles',[]).append(dict(c))
p=next(x for x in d['partialTiles'] if x['tileId']=='r07_c02');p.update(status='16of16_native_geometry_closed_material_external_pending',internalGeometryClosurePassed=True,internalClosurePassed=False,materialStatus='PENDING',geometryClosure=info(out))
s.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'closure':info(out),'ownerReview':info(op),'independentReview':info(ip),'state':info(s)}))

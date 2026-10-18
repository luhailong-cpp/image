from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p): return {'path':str(Path(p).as_posix()),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def verify(pin): assert info(pin['path'])['sha256']==pin['sha256'],pin['path']
s=Z/'west-current-selection-20261012.json';sel=read(s);current=sel['currentTile'];assert current['tileId']=='r05_c02'
indp=Z/'qa/r05_c02_v5_independent_native33_connected_20261013.json';ind=read(indp);owner=read(current['internalReview']['path']);strict=read(current['strictReplay']['path'])
assert ind['passed']==owner['passed']==33 and ind['repair']==owner['repair']==0
assert strict['all16777216PixelsReplayed'] and strict['proof']['verifiedPixelCount']==16777216
for key in ['candidate','record','qaIndex']:
 verify(current[key]);assert current[key]==ind[key]==owner[key]
for key in ['internalReview','strictReplay']:verify(current[key])
assert info(indp)['sha256']=='c50186b4b3927b1d6fc287e5f6ab2ad2fc399c660341ac7fa79854c3a4af87fb'
qa=read(current['qaIndex']['path'])['seamAndJunctionCrops'];assert len(qa)==33
for view in qa:
 verify(view)
 for review in [ind,owner]:
  match=next(x for x in review['items'] if Path(x['path']).name==Path(view['path']).name)
  assert match['sha256']==view['sha256'] and match['status']=='PASS'
closure={'schemaVersion':1,'closedAtUtc':datetime.now(timezone.utc).isoformat(),'tileId':'r05_c02','candidate':current['candidate'],'record':current['record'],'qaIndex':current['qaIndex'],'ownerReview':current['internalReview'],'independentReview':info(indp),'strictReplay':current['strictReplay'],'ownerPass':33,'independentPass':33,'verifiedPixelCount':16777216,'internalClosurePassed':True,'formalAccepted':False,'status':'internal_33_independent_and_owner_PASS_strict_replay_PASS_external_pending','remaining':['External edges and whole-map acceptance remain separate.']}
out=Z/'qa/r05_c02_v5_internal_closure_20261016.json';assert not out.exists();out.write_text(json.dumps(closure,indent=2)+'\n',encoding='utf8')
current.update({'internalClosurePassed':True,'independentReview':info(indp),'closure':info(out),'status':closure['status']})
assert not any(x['tileId']=='r05_c02' for x in sel['completedTiles']);sel['completedTiles'].append(dict(current))
partial=next(x for x in sel['partialTiles'] if x['tileId']=='r05_c02');partial['status']='16of16_native_internal_closed_external_pending';partial['internalClosure']=info(out)
s.write_text(json.dumps(sel,indent=2)+'\n',encoding='utf8')
print(json.dumps({'closure':info(out),'currentTile':current},indent=2))


import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest")
D=Z/'qa/cross_v5_internal_coverage_delta_20261016'
def pin(p):
 p=Path(p);return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def verify(p):
 assert pin(p['path'])['sha256']==p['sha256'],p
idx=json.loads((D/'coverage_index.json').read_text())
notes=json.loads((D/'connected_native_view_notes.json').read_text())
pending=[(t,i) for t in idx['tiles'] for i in t['items'] if i['geometry']=='PENDING_NEW_NATIVE_VIEW']
assert len(pending)==len(notes['items'])==32
cache={}
for t in idx['tiles']:
 verify(t['current']['image']);verify(t['current']['record'])
 cache[t['tileId']]=np.asarray(Image.open(t['current']['image']['path']).convert('RGB'))
review=[]
for n in notes['items']:
 t,e=pending[n['n']]
 verify(e['output'])
 l,u,r,b=e['tileCropBoxHalfOpen']; arr=np.asarray(Image.open(e['output']['path']).convert('RGB'))
 assert np.array_equal(arr,cache[t['tileId']][u:b,l:r]),e['name']
 q={**e,**n,'tileId':t['tileId'],'currentPixelIdentityVerified':True}
 if 'localBox' in n:
  a,c,d,f=n['localBox'];q['issueTileBoxHalfOpen']=[l+a,u+c,l+d,u+f]
 review.append(q)
summary=[]
for t in idx['tiles']:
 fresh=[e for e in review if e['tileId']==t['tileId']]
 fails=sum(e['geometry']!='PASS' for e in fresh)
 summary.append({'tileId':t['tileId'],'current':t['current'],'standardCropCount':33,'reusedPassed':t['reusePassed'],'newViewed':len(fresh),'newGeometryPassed':len(fresh)-fails,'geometryPassedTotal':33-fails,'repairRequiredCrops':fails,'geometryClosurePassed':fails==0,'materialStatus':'PENDING','formalAccepted':False})
out={
 'createdAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/connected_continuation',
 'operation':'Exact current cross v5 internal33 coverage completion; original-sized views only for missing coverage',
 'coverageIndex':pin(D/'coverage_index.json'),'derivationScript':pin(Z/'qa/derive_cross_v5_internal_coverage_20261016.py'),
 'nativeViewNotes':pin(D/'connected_native_view_notes.json'),'viewDetail':'original','generatedOrModifiedArtwork':False,
 'coverageMethod':idx['coverageRule'],'tiles':summary,'newNativeViews':review,
 'uniqueRepairClusters':[
 {'tileId':'r06_c04','nearTileXY':[1024,1580],'crops':[3],'description':'Dark paving groove/bevel interrupted or displaced at vertical core seam; local exact crop required repair/adjudication.'},
 {'tileId':'r06_c04','nearTileXY':[2048,3159],'crops':[7,9,21,30],'description':'Dark paving groove ends abruptly and adjacent bevel has notch at hard surface transition.'},
 {'tileId':'r06_c04','nearTileXY':[3630,3072],'crops':[22],'description':'Upper-left outline of lower stone fades/interrupts before next corner.'}],
 'geometryPassedTotal':sum(x['geometryPassedTotal'] for x in summary),'standardCropTotal':132,'repairRequiredCrops':sum(x['repairRequiredCrops'] for x in summary),
 'internalAllFourGeometryClosurePassed':False,'materialStatus':'PENDING','independentAllFourAccepted':False,'formalAccepted':False,
 'note':'Existing external shared17 geometry PASS is preserved. Current r06c04 internal33 is 27 PASS / 6 repair-required crops covering three defect locations; no more generation authorized by current parent priority. Root/west/right source records untouched.'
}
p=D/'connected_internal33_review.json'
assert not p.exists()
p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'review':pin(p),'summary':summary,'repairClusters':out['uniqueRepairClusters']},ensure_ascii=False))


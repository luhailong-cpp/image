from pathlib import Path
import datetime,hashlib,importlib.util,json,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
S=R.parents[1];ART=S.parents[1];D=R.parent/'c10-seed'
sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'))
spec=importlib.util.spec_from_file_location('mechanical_join',ART/'builtin_q64_production/tools/mechanical_join.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
rec=D/'native.png.generation.json'
r=json.loads(rec.read_text(encoding='utf-8'))
for ent,role in zip(r['references'],['exact native lower-half geometry and material; transparent upper half is missing artwork','canonical whole-city master broad layout only; enlarged reference pixels cannot enter output','user-confirmed art style only']):ent['role']=role
r['sourceCropCoordinateSpace']='global 65536 city pixels; upper missing, lower existing native r09_c10'
rec.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=S/'next_tile_r09_c10/repairs/versions/external-v8/r09_c10.png'
assert sha(source)=='f5a45f15f69104c6f3dfe9f7a855e71f5d142d896cc78ffadbf12b3a57f813e4'
before=np.array(Image.open(source).convert('RGB'))
native=np.array(Image.open(D/'native.png').convert('RGB'))
assert native.shape==(1254,1254,3)
context=native.copy();context[627:]=before[:627,909:2163]
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
dist=np.minimum.reduce([xx,yy,1253-xx,1253-yy])
a=np.clip(dist/96,0,1);mask=np.rint(a*a*(3-2*a)*255).astype(np.uint8)
joined,flow,tone,report=m.registered_join(context,native,mask,max_shift=4,flow_inner=180,flow_full=70,tone_inner=180,tone_full=70,match_tone=True)
O=D/'joined-v1';O.mkdir(exist_ok=False)
Image.fromarray(joined).save(O/'coupled-seed-1254.png')
Image.fromarray(joined[:627]).save(O/'r08_c10-native-fragment-1254x627.png')
Image.fromarray(mask).save(O/'mask.png')
np.save(O/'flow.npy',flow,allow_pickle=False);np.save(O/'tone.npy',tone,allow_pickle=False)
after=before.copy();after[:627,909:2163]=joined[627:]
allowed=np.zeros((4096,4096),bool);allowed[:627,909:2163]=mask[627:]>0
assert not np.any(np.any(after!=before,axis=2)&~allowed)
Image.fromarray(after).save(O/'r09_c10.png')
Q=O/'qa';Q.mkdir()
Image.fromarray(joined[371:883]).save(Q/'new-formal-boundary-y627.png')
Image.fromarray(after[499:755,781:2291]).save(Q/'lower-return.png')
Image.fromarray(after[:755,781:1037]).save(Q/'left-return.png')
Image.fromarray(after[:755,2035:2291]).save(Q/'right-return.png')
Image.fromarray(before[:627,909:2163]).save(Q/'old-native-lower.png')
Image.fromarray(joined[627:]).save(Q/'new-native-lower.png')
record={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'newSourceNative':info(D/'native.png'),'generation':info(rec),'previousLowerTile':info(source),'candidateLowerTile':info(O/'r09_c10.png'),'newUpperFragment':info(O/'r08_c10-native-fragment-1254x627.png'),'coupledSeed':info(O/'coupled-seed-1254.png'),'upperFragmentGlobalLTRB':[37773,32141,39027,32768],'lowerInsertionLTRB':[909,0,2163,627],'operation':report,'mask':info(O/'mask.png'),'flow':info(O/'flow.npy'),'tone':info(O/'tone.npy'),'outsideMaskUnchanged':True,'nativeInputsUpscaled':False,'referenceGuidePixelsInOutput':False,'tileR08C10Complete':False,'formalAccepted':False,'script':info(__file__)}
(O/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ('r09_c10.png','r08_c10-native-fragment-1254x627.png','coupled-seed-1254.png'):
 p=O/name
 p.with_name(p.name+'.generation.json').write_text(json.dumps({'file':str(p),'sha256':sha(p),'derivedFrom':[record['newSourceNative'],record['previousLowerTile']],'sourceGenerationRecord':record['generation'],'assembly':info(O/'assembly.json'),'operation':'native-dimension bounded registration and crop; no enlargement','actualModel':None,'actualQuality':None,'newModelCalls':0,'formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(O),'r09Sha':sha(O/'r09_c10.png'),'operation':report},ensure_ascii=False))

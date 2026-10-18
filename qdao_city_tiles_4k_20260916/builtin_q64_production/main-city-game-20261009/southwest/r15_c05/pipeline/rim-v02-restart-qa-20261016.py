from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parents[2]
d=B/'r15_c05/repairs-resume-20261016/exported-inner-rim-20261016-v02'
r=json.loads((d/'request.json').read_text(encoding='utf-8-sig'))
a=json.loads((d/'integrated-masked-20261016-v01/assembly.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=np.array(Image.open(r['inputContext']).convert('RGB'))
new=np.array(Image.open(a['contextOutput']['file']).convert('RGB'))
mask=np.zeros(old.shape[:2],bool);mask[1156:1210,3072:4326]=True
assert np.array_equal(old[~mask],new[~mask])
assert np.array_equal(old[1140:1156],new[1140:1156])
patch=new[0:1254,3072:4326].copy()
qa=d/'qa';assert not qa.exists();qa.mkdir()
items=[]
def save(name,arr):
 p=qa/name;Image.fromarray(arr).save(p)
 items.append({'file':str(p),'sha256':sha(p),'pixels':[arr.shape[1],arr.shape[0]],'resampling':False})
save('integrated-native-target.png',patch)
save('export-right230.png',patch[:,1024:1254])
save('top.png',patch[:96])
save('bottom.png',patch[-96:])
save('left.png',patch[:,:96])
save('right.png',patch[:,-96:])
save('stripe-before-after-panel.png',np.concatenate([old[1125:1235,3072:4326],new[1125:1235,3072:4326]],axis=0))
m={'inputContext':r['inputContext'],'inputContextSha256':sha(r['inputContext']),'context':a['contextOutput']['file'],'contextSha256':sha(a['contextOutput']['file']),'assembly':str(d/'integrated-masked-20261016-v01/assembly.json'),'assemblySha256':sha(d/'integrated-masked-20261016-v01/assembly.json'),'patchBoxInContext':[3072,0,4326,1254],'maskInContext':[3072,1156,4326,1210],'outsideMaskByteIdentical':True,'outerBlueBoundaryRows1140to1155ByteIdentical':True,'changedPixelCount':int(np.any(old!=new,axis=2).sum()),'sourceResampling':False,'inspectionAssets':items,'formalAccepted':False}
(qa/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(m,ensure_ascii=False))


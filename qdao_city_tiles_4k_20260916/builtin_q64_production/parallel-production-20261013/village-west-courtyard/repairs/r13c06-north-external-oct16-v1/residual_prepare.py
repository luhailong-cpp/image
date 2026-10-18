from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;B=R.parent.parent;Q=R/'final-qa-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
npath=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png';spath=R/'final-candidate-v2/context-native.png'
n=np.asarray(Image.open(npath));s=np.asarray(Image.open(spath));r=[]
for name,l,right,issue in [('N03-residual',2850,3200,[2910,115,3110,145]),('N04-residual',3300,3540,[3340,115,3500,145])]:
    a=np.concatenate([n[4161:4211,l:right],s[115:195,l:right]],axis=0);p=Q/f'{name}.png'
    with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
    assert np.array_equal(a,np.asarray(Image.open(p)))
    r.append({'id':name,'path':str(p),'sha256':sha(p),'dimensions':list(Image.open(p).size),'seamImageY':50,'northContextBox':[l,4161,right,4211],'southContextBox':[l,115,right,195],'globalEvidenceBox':[20365+l,49102,20365+right,49232],'issueSouthContextBox':issue,'issueGlobalBox':[20365+issue[0],49037+issue[1],20365+issue[2],49037+issue[3]],'scale':1,'pixelIdentityMismatch':0})
with (Q/'residual-inputs-v1.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2)
print(json.dumps({'evidence':r}))

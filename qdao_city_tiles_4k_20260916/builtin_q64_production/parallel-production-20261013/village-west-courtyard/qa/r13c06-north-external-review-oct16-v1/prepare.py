from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json,datetime
Q=Path(__file__).resolve().parent;B=Q.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
n=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
s=B/'qa/r13-c06-water-repair-W13-v1/context-native.png'
assert sha(n)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef'
assert sha(s)=='20f0cf314ddb7fb07d307ac3f5fd348638f81c789457674044e0e67ef52534c1'
ni=Image.open(n);si=Image.open(s);assert ni.size==si.size==(4326,4326)
records=[]
for k,x in enumerate([115,1139,2163,3187],1):
    nb=[x,3981,x+1024,4211];sb=[x,115,x+1024,345]
    na=np.asarray(ni.crop(nb));sa=np.asarray(si.crop(sb))
    a=np.concatenate([na,sa],axis=0)
    p=Q/f'north-actual-core-c{k}.png'
    with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
    check=np.asarray(Image.open(p));assert np.array_equal(check[:230],na);assert np.array_equal(check[230:],sa)
    records.append({'segment':k,'path':str(p),'sha256':sha(p),'dimensions':[1024,460],'scale':1,'operation':'exact integer crop of both actual cores, followed by vertical pixel concatenation; no halo, resizing, blending or drawing','northSourceContextBox':nb,'southSourceContextBox':sb,'globalBox':[20365+x,48922,20365+x+1024,49382],'seamImageY':230,'seamGlobalY':49152,'northPixelMismatch':0,'southPixelMismatch':0})
rec={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'northSource':{'tile':'r12_c06','path':str(n),'sha256':sha(n),'globalContextBox':[20365,44941,24691,49267],'actualCoreBox':[115,115,4211,4211]},'southSource':{'tile':'r13_c06','path':str(s),'sha256':sha(s),'globalContextBox':[20365,49037,24691,53363],'actualCoreBox':[115,115,4211,4211]},'seamGlobalY':49152,'crops':records,'formalAccepted':False,'artworkMutated':False,'aiGenerationUsed':False}
with (Q/'inputs-v1.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps({'inputs':str(Q/'inputs-v1.json'),'sha256':sha(Q/'inputs-v1.json'),'segments':4,'dimensionsEach':[1024,460],'coreIdentityMismatch':0}))

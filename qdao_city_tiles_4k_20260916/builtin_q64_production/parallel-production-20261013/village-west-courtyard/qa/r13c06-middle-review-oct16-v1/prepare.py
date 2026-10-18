from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
R=Path(__file__).resolve().parent;B=R.parent.parent;A=B/'qa/r13-c06-water-repair-W13-v1';j=json.loads((A/'assembly.json').read_text());source=A/j['context']['path'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(source)==j['context']['sha256'];im=Image.open(source);sid=A/j['sourceIdMap']['path'];assert sha(sid)==j['sourceIdMap']['sha256'];records=[]
def crop(name,box,scope):
    box=list(map(int,box));p=R/(name+'.png')
    with p.open('xb') as f:im.crop(box).save(f,format='PNG')
    rec={'path':str(p),'sha256':sha(p),'contextBox':box,'dimensions':[box[2]-box[0],box[3]-box[1]],'scale':1,'operation':'exact integer crop','scope':scope};records.append(rec);return rec
for col,x in enumerate([0,1024,2048,3072],1):crop(f'middle-native-c{col}',[x,1536,x+1254,2560],'full new middle coverage plus changed230px overlap')
for col,x in enumerate([1139,2163,3187],1):crop(f'vertical-c{col}',[x-192,1536,x+192,2560],'original vertical seam')
for col,x in enumerate([115,1139,2163,3187],1):crop(f'horizontal-c{col}',[x,1971,x+1024,2355],'original second-row horizontal seam y2163')
rgb=np.asarray(im).astype(float)[1536:2560];ids=np.asarray(Image.open(sid))[1536:2560];scores=np.zeros(ids.shape,float)
for axis in [0,1]:
    a=np.swapaxes(rgb,axis,1);s=np.swapaxes(ids,axis,1);d=np.mean(np.abs(a[:,1:]-a[:,:-1]),axis=2);boundary=s[:,1:]!=s[:,:-1];v=np.zeros_like(d);v[:,1:-1]=np.maximum(0,d[:,1:-1]-(d[:,:-2]+d[:,2:])/2);v*=boundary;v[d<3]=0;arr=np.zeros(s.shape);arr[:,1:]=v;scores=np.maximum(scores,np.swapaxes(arr,axis,1))
scores[:,:115]=0;scores[:,4211:]=0;selected=[]
for k in np.argsort(scores.ravel())[::-1][:10000]:
    y,x=np.unravel_index(k,scores.shape);score=scores[y,x];y+=1536
    if score<=2:break
    if any((x-q['x'])**2+(y-q['y'])**2<220**2 for q in selected):continue
    box=[max(115,x-240),max(1536,y-180),min(4211,x+240),min(2560,y+180)];c=crop(f'boundary-detail-{len(selected)+1}',box,'source-id boundary numerical high contrast diagnostic; inspect only, not automatic failure');selected.append({'x':int(x),'y':int(y),'score':float(score),'crop':c})
    if len(selected)>=8:break
rec={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(source),'sha256':sha(source),'assembly':str(A/'assembly.json'),'assemblySha256':sha(A/'assembly.json'),'sourceIdMap':str(sid),'sourceIdMapSha256':sha(sid),'globalContextBox':j['globalContextBox'],'scope':[115,1766,4211,2560],'changedOverlapScope':[115,1536,4211,1766],'formalAccepted':False,'crops':records,'boundaryRegions':selected}
with (R/'inputs-v1.json').open('x',encoding='utf-8') as f:json.dump(rec,f,indent=2)
print(json.dumps({'sourceSha256':sha(source),'cropCount':len(records),'diagnosticPoints':[{'x':q['x'],'y':q['y'],'score':q['score']} for q in selected]}))

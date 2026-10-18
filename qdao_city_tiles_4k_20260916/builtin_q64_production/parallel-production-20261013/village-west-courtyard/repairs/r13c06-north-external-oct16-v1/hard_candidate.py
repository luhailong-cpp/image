from pathlib import Path
from PIL import Image
import argparse,hashlib,json,datetime,numpy as np
R=Path(__file__).resolve().parent;B=R.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,a):
    with p.open('xb') as f:Image.fromarray(a).save(f,format='PNG')
def dp(cost):
    rows,cols=cost.shape;prev=cost[0].copy();links=np.zeros((rows,cols),np.int8)
    for r in range(1,rows):
        c=np.stack((prev,np.r_[np.inf,prev[:-1]],np.r_[prev[1:],np.inf]));q=np.argmin(c,axis=0)
        links[r]=np.array([0,-1,1],np.int8)[q];prev=cost[r]+np.min(c,axis=0)
    p=np.empty(rows,np.int32);p[-1]=np.argmin(prev)
    for r in range(rows-1,0,-1):p[r-1]=p[r]+links[r,p[r]]
    return p
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--sha256',required=True);p.add_argument('--out',default='hard-v1');a=p.parse_args()
basepath=Path(a.base);assert basepath.parent.name=='r13-c06-water-repair-W19-v1','Only handed-off W19 baseline is authorized'
assert sha(basepath)==a.sha256
assembly=basepath.parent/'assembly.json';aj=json.loads(assembly.read_text())
assert aj['globalContextBox']==[20365,49037,24691,53363]
anchor=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
assert sha(anchor)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef'
base=np.asarray(Image.open(basepath).convert('RGB'));north=np.asarray(Image.open(anchor).convert('RGB'));up=north[4096:4326]
assert base.shape==north.shape==(4326,4326,3)
cost=np.mean((up[115:230].astype(float)-base[115:230].astype(float))**2,axis=2)
path=115+dp(cost.T);mask=np.arange(230)[:,None]<=path[None,:]
candidate=base.copy();candidate[:230][mask]=up[mask]
out=R/a.out;out.mkdir(exist_ok=False)
save(out/'context-native.png',candidate);save(out/'r13_c06.candidate-native-4096.png',candidate[115:4211,115:4211])
save(out/'north-source-mask.png',(mask*255).astype(np.uint8))
source_id=np.zeros(base.shape[:2],np.uint8);source_id[:230][mask]=1;save(out/'source-layer-id.png',source_id)
replay=base.copy();replay[:230][mask]=up[mask]
checks=[]
for k,x in enumerate([115,1139,2163,3187],1):
    # Both actual core portions, plus enough south pixels to inspect the moved DP boundary.
    qa=np.concatenate((north[3981:4211,x:x+1024],candidate[115:575,x:x+1024]),axis=0)
    q=out/f'actual-core-join-c{k}.png';save(q,qa)
    checks.append({'path':str(q),'sha256':sha(q),'size':[1024,690],'seamImageY':230,'northContextBox':[x,3981,x+1024,4211],'southContextBox':[x,115,x+1024,575],'globalBox':[20365+x,48922,20365+x+1024,49612]})
for k,x in enumerate([0,1024,2048,3072],1):save(out/f'native-boundary-c{k}.png',candidate[:575,x:x+1254])
proof={'replayMismatch':int(np.any(replay!=candidate,axis=2).sum()),'outsideOverlapChanges':int(np.any(candidate[230:]!=base[230:],axis=2).sum()),'north115Mismatch':int(np.any(candidate[:115]!=up[:115],axis=2).sum()),'anchorHashUnchanged':sha(anchor)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef','allPixelsFromSource':True}
rec={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c06','status':'pending-visual-QA','formalAccepted':False,'base':{'path':str(basepath),'sha256':sha(basepath),'assembly':str(assembly),'assemblySha256':sha(assembly)},'northAnchor':{'path':str(anchor),'sha256':sha(anchor),'globalContextBox':[20365,44941,24691,49267],'trace':str(anchor.parent/'assembly.json'),'traceSha256':sha(anchor.parent/'assembly.json'),'deliveryManifest':str(anchor.parent.parent/'delivery-manifest-v1.json'),'deliveryManifestSha256':sha(anchor.parent.parent/'delivery-manifest-v1.json')},'globalContextBox':[20365,49037,24691,53363],'operation':'binary native source selection at identical global pixel coordinates; no AI, resizing, blending, blur or painting','sourceLegend':[{'sourceLayerId':0,'path':str(basepath),'sha256':sha(basepath),'globalContextBox':[20365,49037,24691,53363],'provenance':'Linked complete W19 native assembly'},{'sourceLayerId':1,'path':str(anchor),'sha256':sha(anchor),'globalContextBox':[20365,44941,24691,49267],'provenance':'Linked frozen r12 native trace chain'}],'mask':{'path':str(out/'north-source-mask.png'),'sha256':sha(out/'north-source-mask.png'),'globalBox':[20365,49037,24691,49267],'values':[0,255]},'sourceLayerIdMap':{'path':str(out/'source-layer-id.png'),'sha256':sha(out/'source-layer-id.png')},'pathYInR13Context':path.tolist(),'pathRange':[int(path.min()),int(path.max())],'context':{'path':str(out/'context-native.png'),'sha256':sha(out/'context-native.png')},'tile4096':{'path':str(out/'r13_c06.candidate-native-4096.png'),'sha256':sha(out/'r13_c06.candidate-native-4096.png')},'proof':proof,'actualCoreJoinChecks':checks,'requiresVisualCheck':['actual core y115 join','entire moved selection boundary y115..229','vertical junctions of prior native patches','r13 unchanged lower side']}
with (out/'assembly.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps({'out':str(out),'contextSha256':rec['context']['sha256'],'tileSha256':rec['tile4096']['sha256'],'pathRange':rec['pathRange'],'proof':proof}))

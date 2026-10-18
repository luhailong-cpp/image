from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
R=Path(__file__).resolve().parent;B=R.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
assembly=Path(sys.argv[1]);version=sys.argv[2];a=read(assembly);own=np.asarray(Image.open(a['context']['path']).convert('RGB'));west=np.asarray(Image.open(a['anchor']['path']).convert('RGB'))
out=B/f'qa/r13-c07-west-final-inspection-oct16b-{version}';out.mkdir(exist_ok=True);crops=[]
join=np.concatenate((west[:,3584:4211],own[:,115:742]),axis=1)
for i,y in enumerate([0,1024,2048,3072,794,1818,2842],1):
    h=1254 if i<=4 else 690;p=out/f'band-{i:02d}.png';Image.fromarray(join[y:y+h]).save(p)
    crops.append(dict(pin(p),id=f'band-{i:02d}',contextNativeBox=[-512,y,742,y+h],actualCoreJoinImageX=627,scale=1,reviewed=False))
southpath=B.parents[1]/'fishing-village-game-20261009/southwest/qa/pair-r14c06-r14c07-v3-r14_c07-context-native.png';south=np.asarray(Image.open(southpath).convert('RGB'))
southjoin=np.concatenate((own[3584:4211,:1254],south[115:742,:1254]),axis=0);p=out/'south-west-corner.png';Image.fromarray(southjoin).save(p);crops.append(dict(pin(p),id='south-west-corner',contextNativeBox=[0,3584,1254,4838],actualCoreJoinImageY=627,scale=1,reviewed=False))
prior=read(B/'qa/r13-c07-internal-inspection-oct16b-v1/inspection-manifest.json');baseline=B/'repairs/r13c07-south-external-oct16b-v1/south-c04-v01-assembly-v2/context-native.png';base=np.asarray(Image.open(baseline).convert('RGB'));reused=[]
for c in prior['nativeCrops']:
    box=c.get('contextNativeBox',c.get('contextBox'));x,y,xx,yy=box
    same=np.array_equal(own[y:yy,x:xx],base[y:yy,x:xx])
    if same:reused.append(dict(id=c['id'],unchangedSinceSouthCheckpoint=True,accepted=c['id']!='vertical-r01-c03'))
    else:
        p=out/(c['id']+'.png');Image.fromarray(own[y:yy,x:xx]).save(p);crops.append(dict(pin(p),id=c['id'],contextNativeBox=box,scale=1,reviewed=False))
js(out/'manifest.json',{'assembly':pin(assembly),'candidate':a['candidate'],'context':a['context'],'westAnchor':a['anchor'],'southAnchor':pin(southpath),'crops':crops,'reusedInternalCrops':reused,'formalAccepted':False});print(json.dumps({'manifest':pin(out/'manifest.json'),'crops':[c['id'] for c in crops],'reused':len(reused)}))

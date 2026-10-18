from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
own=B/'repairs/r13c07-west-external-oct16b-v1/west-r04-v01-assembly-v2/r13_c07.candidate.png';east=B.parents[1]/'fishing-village-game-20261009/southeast/r13_c08/processed/colorpass-resume-20261012-v2/r13_c08-colorpass-candidate.png'
assert sha(own)=='22b98bc63e25db7e9d6c7fc5e3473fb69e357d589fc47890a8613e4ad33d565a'
assert sha(east)=='7a9a7de302ae3640be1ab1e8fcb53af1c9642737a3734439acb56b5d450ee589'
a=np.asarray(Image.open(own).convert('RGB'));b=np.asarray(Image.open(east).convert('RGB'));assert a.shape==b.shape==(4096,4096,3)
out=B/'qa/r13-c07-east-actualcorejoin-oct16b-v1';out.mkdir(exist_ok=False);join=np.concatenate((a[:,-345:],b[:,:345]),axis=1);crops=[]
for i,y in enumerate([0,1024,2048,3072,679,1703,2727],1):
    h=1024 if i<=4 else 690;p=out/f'band-{i:02d}.png';Image.fromarray(join[y:y+h]).save(p);crops.append(dict(pin(p),id=f'band-{i:02d}',coreY=y,actualCoreJoinImageX=345,scale=1,reviewed=False))
js(out/'manifest.json',{'ownCandidate':pin(own),'eastCandidate':pin(east),'eastCandidateProvenance':'current selected owner colorpass processed candidate, not a raw native generator output','eastFrozenExternalPin':False,'operation':'exact native-scale core strips; integer concatenation only','crops':crops,'formalAccepted':False})
print(json.dumps(pin(out/'manifest.json')))

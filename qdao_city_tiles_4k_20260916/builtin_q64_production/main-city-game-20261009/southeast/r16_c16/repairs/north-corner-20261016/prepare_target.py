from pathlib import Path
import json,hashlib,datetime
from PIL import Image,ImageDraw
import numpy as np
T=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent;Z=T.parent
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ev(p):return dict(path=str(p),sha256=sha(p))
latest=rd(T/'candidate/latest-assembly.json');north=rd(Z/'r15_c16/candidate/latest-assembly.json')
assert latest['candidate']['sha256']=='fa9ff5a51638c2664c2ffe690d93fd7fc5ca8bfc911867cdb532c13069f7fc5e'
assert sha(latest['candidate']['path'])==latest['candidate']['sha256']
a=Image.open(latest['candidate']['path']).convert('RGB');b=Image.open(north['candidate']['path']).convert('RGB')
old=Image.open(Z/'r15_c16/candidate/r15_c16-4k-candidate-7783279d21b0e091e554.png').convert('RGB')
assert np.array_equal(np.array(b.crop((0,3776,4096,4096))),np.array(old.crop((0,3776,4096,4096))))
target=Image.new('RGB',(1254,1254));target.paste(b.crop((750,3776,2004,4096)),(0,0));target.paste(a.crop((750,0,2004,934)),(0,320))
p=D/'target-1254.png';assert not p.exists();target.save(p)
marked=target.copy();ImageDraw.Draw(marked).rectangle((300,320,899,919),outline=(255,0,255),width=3);marked.save(D/'target-marked.png')
prep=dict(schemaVersion=1,tile='r16_c16',id='N02-north-corner',attempt=1,preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),route='builtin',actualModel=None,expectedNativeSize=[1254,1254],base=latest['candidate'],baseContext=latest['context'],north=north['candidate'],northPreviousBottom320Exact=True,target=ev(p),markedGuide=ev(D/'target-marked.png'),contextOriginInCore=[750,-320],sourceCrop=[300,320,900,920],destinationCoreBox=[1050,0,1650,600],pixelSources=[dict(source=north['candidate'],sourceCrop=[750,3776,2004,4096],target=[0,0,1254,320]),dict(source=latest['candidate'],sourceCrop=[750,0,2004,934],target=[0,320,1254,1254])],constraints='Keep all child pixels outside x1050..1649,y0..599 exact, and all north pixels immutable.',resampling=False,formalAccepted=False)
(D/'preparation.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(target=ev(p),preparation=ev(D/'preparation.json'))))


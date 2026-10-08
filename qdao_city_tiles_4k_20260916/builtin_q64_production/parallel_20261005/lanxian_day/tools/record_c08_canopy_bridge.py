from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;T=ROOT/'r09_c08';D=T/'canopy-repair'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
rp=D/'bridge.receipt01.json';rq=D/'bridge.actual-request01.json';r=read(rp);request=read(rq);s=Path(r['sourceOutputPath']);assert r['prompt']==request['prompt'] and r['references']==request['references']
with Image.open(s) as im:assert im.size==(1254,1254) and im.format=='PNG';mode=im.mode
refs=[]
for rr in r['references']:
 p=Path(rr['path']);refs.append({**rr,'sha256':sha(p),'pixels':list(Image.open(p).size)})
pf=D/'bridge.actual-prompt01.txt';gp=D/'bridge.generation01.json';assert not pf.exists() and not gp.exists();pf.write_text(r['prompt'],encoding='utf-8')
g={'schemaVersion':1,'file':str(s),'sha256':sha(s),'pixels':[1254,1254],'width':1254,'height':1254,'format':'PNG','mode':mode,'generatedAt':r['generatedAt'],'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(T/'jobs/r01_c03.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'prompt':r['prompt'],'referenced_image_paths':[x['path'] for x in r['references']],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed tool exposes no model/quality selectors and no verified backend metadata.','sourceJob':str(rq),'sourceJobSha256':sha(rq),'sourceJobKind':'actual-request','prompt':r['prompt'],'promptFile':str(pf),'promptSha256':sha(pf),'references':refs,'evidence':{'sourceOutputPath':str(s),'sourceOutputSha256':sha(s),'toolResultPath':str(rp),'toolResultSha256':sha(rp)},'inputDerivation':{'file':str(D/'north-south-board1254.manifest.json'),'sha256':sha(D/'north-south-board1254.manifest.json')},'role':'Native AI repair source with joint-centered framing; may supply mapped south canopy pixels only after real-neighbor review. Not a whole native cell or enlarged guide.','guideOnly':False,'finalArt':False,'directlyInSelectedAssembly':False,'formalAccepted':False}
gp.write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'record':str(gp),'sha256':sha(gp),'sourceOutputSha256':sha(s)}))

import json,sys,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
BASE=Path(__file__).resolve().parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
jobs=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
for j in jobs:
    native=BASE/j['nativeFile']; out=BASE/j['exportFile']; native.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(j['nativeHostPath'],native)
    with Image.open(native) as im:
        assert im.mode=='RGBA',im.mode
        assert min(im.size)>=1024 and im.width==im.height,im.size
        assert im.getchannel('A').getextrema()==(0,255)
        sz=list(im.size); bbox=list(im.getchannel('A').getbbox())
        if im.size!=(1024,1024): im.resize((1024,1024),Image.Resampling.LANCZOS).save(out)
        else: shutil.copyfile(native,out)
    refs=[{'path':p,'sha256':sha(p),'role':r} for p,r in zip(j['refs'],['editTarget','characterIdentity','bambooSameDirectionFootAnatomy','approvedStyle'])]
    rec={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'action':'run','direction':j['direction'],'frame':j['frame'],'version':j['version'],'route':'host-managed builtin image_gen.imagegen','configurationTarget':{'model':'gpt-image-2.5-sunburst','quality':'max'},'actualSubmitted':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':j['refs'],'prompt':j['prompt']},'actualReturned':{'model':None,'quality':None,'status':'unconfirmed: tool returned no model/quality metadata'},'references':refs,'promptFile':j['promptFile'],'receipt':j['receipt'],'nativeFile':j['nativeFile'],'nativeSha256':sha(native),'nativeSize':sz,'nativeAlphaBBox':bbox,'exportFile':j['exportFile'],'exportSha256':sha(out),'exportSize':[1024,1024],'transform':{'kind':'whole-canvas proportional resize','size':[1024,1024],'resampler':'LANCZOS','translation':[0,0],'crop':None},'reviewStatus':'candidate pending actual image review'}
    Path(str(native)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    Path(str(out)+'.generation.json').write_text(json.dumps({**rec,'derivedFromRecord':str(native.relative_to(BASE))+'.generation.json'},ensure_ascii=False,indent=2),encoding='utf-8')
    (BASE/j['promptFile']).write_text(j['prompt'],encoding='utf-8')
    print(json.dumps({'direction':j['direction'],'frame':j['frame'],'export':str(out),'nativeSize':sz,'alphaBBox':bbox},ensure_ascii=False))


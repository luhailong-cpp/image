from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json,re,shutil,sys
P=Path(__file__).resolve().parent;name=sys.argv[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
receipt=read(P/(name+'.tool-response.json'));request=read(P/(name+'.request.json'));pre=read(P/(name+'.preflight.json'))
assert receipt['request']==request
for ref in pre['references']:assert sha(ref['file'])==ref['sha256']
source=Path(re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S).group(1));im=Image.open(source);im.load();assert im.size==(1254,1254) and im.format=='PNG'
native=P/(name+'.native.png')
with source.open('rb') as a,native.open('xb') as b:shutil.copyfileobj(a,b)
assert sha(native)==sha(source)
rec={'schemaVersion':4,'file':str(native),'sha256':sha(native),'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':pre['configSnapshot'],'configSnapshotFile':pre['configSnapshotFile'],'actualRequest':request,'request':info(P/(name+'.request.json')),'preflight':info(P/(name+'.preflight.json')),'references':pre['references'],'editBefore':pre['references'][0],'sourceCandidate':pre['sourceCandidate'],'sourceAssembly':pre['sourceAssembly'],'fixedBottomNeighbor':pre['fixedBottomNeighbor'],'canvasBoxLTRB':pre['canvasBoxLTRB'],'evidence':info(P/(name+'.tool-response.json')),'toolOutputPath':str(source),'toolOutputSha256':sha(source),'generatedAt':None,'observedCompletionAt':receipt['observedCompletionAt'],'savedAtUtc':datetime.now(timezone.utc).isoformat(),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed tool response has image_url and output_hint only; no verifiable model, quality or generated timestamp','originalNativeBytesPreserved':True,'resampled':False,'finalArtUpscaled':False,'accepted':False,'visualStatus':'pending_masked_application_and_QA'}
with (P/(name+'.generation.json')).open('x',encoding='utf8',newline='\n') as f:json.dump(rec,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'native':info(native),'record':info(P/(name+'.generation.json'))}))

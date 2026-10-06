from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;S=O.parent
host=Path(r'C:\Users\luyua\.codex\generated_images\01a10bad-d273-7922-8463-920d6ebf1878\exec-89045c73-7e69-4ac4-8002-74ea85a77122.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
shutil.copyfile(host,O/'native.png')
req=json.loads((O/'request.json').read_text());receipt=json.loads((O/'tool-response.json').read_text())
raw=np.array(Image.open(O/'native.png').convert('RGB'));ctx=np.array(Image.open(O/'context.png').convert('RGBA'))
assert raw.shape==(1254,1254,3) and sha(host)==sha(O/'native.png')
rec={'file':str(O/'native.png'),'sha256':sha(O/'native.png'),'generatedAt':None,'observedCompletionAt':receipt['observedCompletionAt'],
 'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':req['configSnapshot'],
 'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,
 'unverifiedReason':'Host-managed; tool exposes no model/quality/size selector and returns no verifiable backend version/quality. Server creation time unknown.',
 'prompt':str(O/'prompt.txt'),'references':req['references'],'referenceRoles':req['referenceRoles'],
 'evidence':{'actualToolResponse':info(O/'tool-response.json'),'actualRequest':info(O/'request.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},
 'candidateStatus':'native_return_pending_review','countsAsComplete4KTile':False,'formalAccepted':False}
save(O/'native.png.generation.json',rec)
missing=ctx[:,:,3]==0;joined=ctx[:,:,:3].copy();joined[missing]=raw[missing]
Image.fromarray(joined).save(O/'joined.png')
Image.fromarray(missing.astype(np.uint8)*255).save(O/'mask.png')
assert np.array_equal(joined[~missing],ctx[:,:,:3][~missing])
save(O/'assembly.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Restore all fixed target pixels, insert only native pixels in the requested transparent repair rectangle at1:1. No scaling, registration, color correction or feathering.',
 'derivedFrom':[info(O/'native.png'),info(O/'context.png')],'mask':info(O/'mask.png'),'output':info(O/'joined.png'),
 'repairMaskLTRB':req['repairMaskLTRB'],'insertedNativePixels':int(missing.sum()),'knownPixelsUnchanged':True,'script':info(Path(__file__)),'localAccepted':False,'formalAccepted':False})
save(O/'joined.png.generation.json',{'output':info(O/'joined.png'),'derivedFrom':[info(O/'native.png'),info(O/'context.png')],'assembly':info(O/'assembly.json'),'newModelCalls':0})
qa=O/'qa';qa.mkdir(exist_ok=True)
for n,b in [('repair-surround',(130,440,570,1020)),('left-return',(150,500,310,960)),('right-return',(390,500,550,960)),('top-return',(190,470,510,610)),('bottom-return',(190,850,510,990)),('top-left-corner',(0,300,350,490))]:
 Image.fromarray(joined).crop(b).save(qa/(n+'.png'))
save(qa/'manifest.json',[{**info(p),'originalPixelScale':1} for p in qa.glob('*.png')])
print(json.dumps({'native':info(O/'native.png'),'joined':info(O/'joined.png'),'insertedNativePixels':int(missing.sum())}))

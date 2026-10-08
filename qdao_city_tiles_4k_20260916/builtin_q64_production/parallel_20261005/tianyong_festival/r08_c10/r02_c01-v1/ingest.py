from pathlib import Path
import hashlib,json,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,v):
 with (O/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
rec=read(O/'tool-response.json');host=Path(rec['hostPath']);assert not (O/'native.png').exists()
with Image.open(host) as im:im.verify()
shutil.copy2(host,O/'native.png');assert sha(host)==sha(O/'native.png')
with Image.open(O/'native.png') as im:
 assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
 raw=np.asarray(im.convert('RGB'))
req=read(O/'request.json');prep=read(O/'preparation.json')
write('native.png.generation.json',{**info(O/'native.png'),'generatedAt':None,'observedCompletionAt':rec['hostObservedFinishedAtUtc'],'recordSavedAtUtc':datetime.now(timezone.utc).isoformat(),'timestampSemantics':'Actual server generation time undisclosed; host completion observation saved separately','width':1254,'height':1254,'format':'PNG','route':'builtin','tool':'image_gen.imagegen','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool exposes no model/quality selector and returns no verifiable model/quality metadata','prompt':info(O/'prompt.txt'),'references':prep['references'],'globalCropLTRB':req['globalCropLTRB'],'tileLocalCropLTRB':req['tileLocalCropLTRB'],'evidence':{'actualRequest':info(O/'request.json'),'actualToolResponse':info(O/'tool-response.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'resizedAfterGeneration':False,'upscaled':False,'formalAccepted':False})
ctx=np.asarray(Image.open(O/'original-context.png').convert('RGBA'));known=ctx[:,:,3]==255;hard=raw.copy();hard[known]=ctx[:,:,:3][known]
qa=[('qa-hard-native-return.png',[0,0,1254,1254]),('qa-hard-left.png',[0,0,320,1254]),('qa-hard-right.png',[904,0,1254,1254]),('qa-hard-top.png',[0,0,1254,380]),('qa-hard-bottom.png',[0,884,1254,1254])]
for n,b in qa:
 Image.fromarray(hard).crop(b).save(O/n)
 write(n+'.generation.json',{**info(O/n),'derivedFrom':[info(O/'native.png'),info(O/'original-context.png')],'operation':'Hard return diagnostic composed from actual source pixels and raw generation; not accepted assembly','cropLTRB':b,'newModelCalls':0})
stats=[]
for n,b in [('left',[0,230,115,1024]),('right',[1024,230,1254,1024]),('top',[115,0,1024,230]),('bottom',[115,1024,1024,1254])]:
 x0,y0,x1,y1=b;d=raw[y0:y1,x0:x1].astype(np.float32)-ctx[y0:y1,x0:x1,:3].astype(np.float32)
 stats.append({'region':n,'cropLTRB':b,'meanDeltaRGB':d.mean((0,1)).tolist(),'meanAbsRGB':np.abs(d).mean((0,1)).tolist(),'maxAbsRGB':np.abs(d).max((0,1)).tolist()})
write('comparison.json',{'native':info(O/'native.png'),'source':info(O/'original-context.png'),'stats':stats,'caveat':'Geometry and texture need native visual review; numeric similarity is not acceptance','formalAccepted':False})
print(json.dumps({'native':info(O/'native.png'),'stats':stats}))

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
host=Path('C:/Users/luyua/.codex/generated_images/01a10bae-bc72-7652-9e32-7581b813d53f/exec-0a98e53d-35f2-4adb-b917-a219ab4e9887.png')
assert not (OUT/'native.png').exists()
with Image.open(host) as im:im.verify()
shutil.copy2(host,OUT/'native.png');assert sha(host)==sha(OUT/'native.png')
with Image.open(OUT/'native.png') as im:
    im.load();pixels=list(im.size);fmt=im.format;mode=im.mode
    assert pixels==[1254,1254]
    assert mode!='RGBA' or im.getextrema()[3]==(255,255)
    native=im.convert('RGB')
req=read(OUT/'request.json');prep=read(OUT/'preparation.json');receipt=read(OUT/'tool-response.json')
write('native.png.generation.json',{'file':str(OUT/'native.png'),'sha256':sha(OUT/'native.png'),'generatedAt':None,'observedCompletionAt':receipt['hostObservedFinishedAtUtc'],'recordSavedAtUtc':datetime.now(timezone.utc).isoformat(),'timestampSemantics':'Actual host completion observed; server generation time unknown','width':1254,'height':1254,'format':fmt,'mode':mode,'route':'builtin','tool':'image_gen.imagegen','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality/size selectors or returned verifiable model/quality metadata','prompt':info(OUT/'prompt.txt'),'references':prep['references'],'globalCropLTRB':req['globalCropLTRB'],'tileLocalCropLTRB':req['tileLocalCropLTRB'],'evidence':{'actualRequest':info(OUT/'request.json'),'actualToolResponse':info(OUT/'tool-response.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'resizedAfterGeneration':False,'upscaled':False,'formalAccepted':False,'countsAsComplete4KTile':False})
context=Image.open(OUT/'context.png').convert('RGB')
board=Image.new('RGB',(1254,1254));board.paste(context.crop((0,627,1254,1254)),(0,0));board.paste(native.crop((0,627,1254,1254)),(0,627));board.save(OUT/'comparison-bottom627-original-above-raw-below.png')
hard=Image.new('RGB',(1254,256));hard.paste(native.crop((0,499,1254,627)),(0,0));hard.paste(context.crop((0,627,1254,755)),(0,128));hard.save(OUT/'comparison-hard-return-y627.png')
raw=np.asarray(native).astype(float);ctx=np.asarray(context).astype(float);delta=np.abs(raw[627:]-ctx[627:]);lum=lambda a:a@np.array([.2126,.7152,.0722])
measurements=[]
for y in [631,700,850,980]:
    a=np.diff(lum(ctx[y-3:y+4]).mean(axis=0));b=np.diff(lum(raw[y-3:y+4]).mean(axis=0))
    for lo,hi in [(70,180),(330,450),(450,570),(700,815),(840,960),(1100,1240)]:
        e=lo+int(np.argmax(np.abs(a[lo:hi])));nlo=max(lo,e-40);nhi=min(hi,e+41);re=nlo+int(np.argmax(np.sign(a[e])*b[nlo:nhi]))
        measurements.append({'y':y,'xSearchRange':[lo,hi],'contextStrongestEdgeX':e,'rawSamePolarityStrongestEdgeX':re,'rawMinusContextX':re-e})
qa=[]
for name in ['comparison-bottom627-original-above-raw-below.png','comparison-hard-return-y627.png']:
    item=info(OUT/name);qa.append(item)
    write(name+'.generation.json',{'file':item['file'],'sha256':item['sha256'],'derivedFrom':[info(OUT/'native.png'),info(OUT/'context.png')],'operation':'1:1 exact crops juxtaposed for inspection; no resampling, no production pixels','newModelCalls':0})
write('comparison.json',{'native':info(OUT/'native.png'),'context':info(OUT/'context.png'),'knownRegionLTRB':[0,627,1254,1254],'knownPixels':1254*627,'meanAbsRGB':delta.mean(axis=(0,1)).tolist(),'maxAbsRGB':delta.max(axis=(0,1)).tolist(),'measurements':measurements,'diagnosticCaveat':'Matching polarity strongest luminance edge may differ with contrast. Not an acceptance or registration method.','qa':qa,'resampling':False,'blending':False,'joinedIntoCurrent':False})
print(json.dumps({'native':info(OUT/'native.png'),'meanAbsRGB':delta.mean(axis=(0,1)).tolist(),'row631Offsets':[m['rawMinusContextX'] for m in measurements if m['y']==631]}))

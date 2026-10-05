from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
from PIL import Image
import numpy as np

OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,data):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')

host=Path('C:/Users/luyua/.codex/generated_images/01a10bae-bc72-7652-9e32-7581b813d53f/exec-cc0218af-e6a2-4fc5-9d6f-d21cd9a9c7e1.png')
request=read(OUT/'request.json');prep=read(OUT/'preparation.json');receipt=read(OUT/'tool-response.json')
native=OUT/'native.png'
assert not native.exists()
with Image.open(host) as im:im.verify()
shutil.copy2(host,native)
assert sha(host)==sha(native)
with Image.open(native) as im:
    im.load();pixels=list(im.size);fmt=im.format;mode=im.mode
    assert pixels==[1254,1254]
    assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
    raw=im.convert('RGB')
record={'file':str(native),'sha256':sha(native),'generatedAt':None,'observedCompletionAt':receipt['hostObservedFinishedAtUtc'],'recordSavedAtUtc':datetime.now(timezone.utc).isoformat(),'timestampSemantics':'Tool completion observed by client; server generation time not disclosed','width':pixels[0],'height':pixels[1],'format':fmt,'mode':mode,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':request['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality/size selectors and no verifiable returned model or quality metadata','prompt':info(OUT/'prompt.txt'),'references':prep['references'],'globalCropLTRB':request['globalCropLTRB'],'tileLocalCropLTRB':request['tileLocalCropLTRB'],'evidence':{'actualRequest':info(OUT/'request.json'),'actualToolResponse':info(OUT/'tool-response.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'resizedAfterGeneration':False,'upscaled':False,'candidateStatus':'unreviewed_native_return','countsAsComplete4KTile':False,'formalAccepted':False}
write('native.png.generation.json',record)
context=Image.open(OUT/'context.png').convert('RGBA')
old=context.convert('RGB')
comparison=Image.new('RGB',(1254,460))
comparison.paste(old.crop((0,1024,1254,1254)),(0,0))
comparison.paste(raw.crop((0,1024,1254,1254)),(0,230))
comparison.save(OUT/'comparison-bottom230-original-above-raw-below.png')
hard=Image.new('RGB',(1254,256))
hard.paste(raw.crop((0,896,1254,1024)),(0,0))
hard.paste(old.crop((0,1024,1254,1152)),(0,128))
hard.save(OUT/'comparison-hard-return-y1024.png')
raw_arr=np.asarray(raw).astype(np.int16);old_arr=np.asarray(old).astype(np.int16)
delta=np.abs(raw_arr[1024:]-old_arr[1024:])
data={'native':info(native),'context':info(OUT/'context.png'),'scope':'Known bottom230 rows only; mechanical pixel difference does not decide visual continuity','knownRegionLTRB':[0,1024,1254,1254],'knownPixelCount':1254*230,'meanAbsRGB':delta.mean(axis=(0,1)).tolist(),'maxAbsRGB':delta.max(axis=(0,1)).tolist(),'exactRGBPixelFraction':float(np.mean(np.all(delta==0,axis=2))),'qa':[{'file':str(OUT/'comparison-bottom230-original-above-raw-below.png'),'sha256':sha(OUT/'comparison-bottom230-original-above-raw-below.png'),'size':[1254,460],'sections':[{'source':info(OUT/'context.png'),'cropLTRB':[0,1024,1254,1254],'pasteXY':[0,0]},{'source':info(native),'cropLTRB':[0,1024,1254,1254],'pasteXY':[0,230]}]},{'file':str(OUT/'comparison-hard-return-y1024.png'),'sha256':sha(OUT/'comparison-hard-return-y1024.png'),'size':[1254,256],'sections':[{'source':info(native),'cropLTRB':[0,896,1254,1024],'pasteXY':[0,0]},{'source':info(OUT/'context.png'),'cropLTRB':[0,1024,1254,1152],'pasteXY':[0,128]}]}],'pixelScale':'1:1','resampling':False,'blending':False,'joinedIntoCurrent':False,'visualAccepted':None}
write('comparison.json',data)
for item in data['qa']:
    write(Path(item['file']).name+'.generation.json',{'file':item['file'],'sha256':item['sha256'],'derivedFrom':[info(native),info(OUT/'context.png')],'operation':'Exact crops assembled for review at original pixel scale. No resampling. Not production artwork.','newModelCalls':0,'parts':item['sections']})
print(json.dumps({'native':info(native),'pixels':pixels,'knownRegionMeanAbsRGB':data['meanAbsRGB'],'copiedByteIdentically':True}))

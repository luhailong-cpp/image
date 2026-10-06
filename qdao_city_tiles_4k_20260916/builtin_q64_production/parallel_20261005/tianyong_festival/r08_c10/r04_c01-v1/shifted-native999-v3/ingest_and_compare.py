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
receipt=read(OUT/'tool-response.json');host=Path(receipt['hostPath'])
assert not (OUT/'native.png').exists()
with Image.open(host) as im:im.verify()
shutil.copy2(host,OUT/'native.png');assert sha(host)==sha(OUT/'native.png')
with Image.open(OUT/'native.png') as im:
    im.load();size=list(im.size);fmt=im.format;mode=im.mode
    assert size==[1254,1254]
    assert mode!='RGBA' or im.getextrema()[3]==(255,255)
    native=im.convert('RGB')
req=read(OUT/'request.json');prep=read(OUT/'preparation.json')
write('native.png.generation.json',{'file':str(OUT/'native.png'),'sha256':sha(OUT/'native.png'),'generatedAt':None,'observedCompletionAt':receipt['hostObservedFinishedAtUtc'],'recordSavedAtUtc':datetime.now(timezone.utc).isoformat(),'timestampSemantics':'Server generation time unknown; host-observed completion recorded separately','width':1254,'height':1254,'format':fmt,'mode':mode,'route':'builtin','tool':'image_gen.imagegen','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; no model/quality/size selectors or verifiable returned model/quality metadata','prompt':info(OUT/'prompt.txt'),'references':prep['references'],'globalCropLTRB':req['globalCropLTRB'],'tileLocalCropLTRB':req['tileLocalCropLTRB'],'evidence':{'actualRequest':info(OUT/'request.json'),'actualToolResponse':info(OUT/'tool-response.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'resizedAfterGeneration':False,'upscaled':False,'formalAccepted':False,'countsAsComplete4KTile':False})
ctx=Image.open(OUT/'original-context.png').convert('RGB');edit=Image.open(OUT/'context.png').convert('RGB')
a=np.asarray(ctx,dtype=float);b=np.asarray(native,dtype=float);ec=np.asarray(edit,dtype=float)
known=np.asarray(Image.open(OUT/'original-context.png'))[:,:,3]==255
hard=b.copy();hard[known]=a[known]
Image.fromarray(hard.astype(np.uint8)).save(OUT/'qa-hard-original-return.png')
qa={'qa-bottom-original-above-raw-below.png':np.concatenate([a[255:511],b[255:511]],0),'qa-hard-bottom-y255.png':hard[127:383],'qa-upper-original-above-raw-below.png':np.concatenate([ec[:64],b[:64]],0),'qa-hard-left-x115.png':hard[:255,:243],'qa-hard-right-x1024.png':hard[:255,896:]}
for name,pixels in qa.items():Image.fromarray(pixels.astype(np.uint8)).save(OUT/name)
lum=lambda p:p@np.array([.2126,.7152,.0722]);al=lum(a);bl=lum(b);measure=[]
for y in [259,260,296,336,365,428,505,628,755]:
 aa=np.diff(al[y-3:y+4].mean(0));bb=np.diff(bl[y-3:y+4].mean(0))
 # Track distinct structures: left gray transition, right face-to-dark, right dark-to-ivory.
 for label,lo,hi,polarity in [('left_gray',40,300,-1),('right_dark_to_ivory',300,950,1),('right_gray_to_dark',450,875,-1)]:
  e=lo+int(np.argmax(polarity*aa[lo:hi]));l=max(lo,e-60);h=min(hi,e+61);r=l+int(np.argmax(polarity*bb[l:h]))
  measure.append({'edge':label,'y':y,'contextX':e,'rawX':r,'rawMinusContextX':r-e,'contextGradient':float(aa[e]),'rawGradient':float(bb[r])})
regions=[]
for label,box in [('left',[0,0,115,255]),('right',[1024,0,1254,255]),('bottom',[0,255,1254,1254]),('top_retained',[115,0,1024,64])]:
 x0,y0,x1,y1=box;ref=ec if label=='top_retained' else a;d=np.abs(ref[y0:y1,x0:x1]-b[y0:y1,x0:x1]);regions.append({'region':label,'box':box,'meanAbsRGB':d.mean((0,1)).tolist(),'maxAbsRGB':d.max((0,1)).tolist()})
faces=[]
for label,box in [('gray',[350,261,700,356]),('top_retained_gray',[350,5,700,55])]:
 x0,y0,x1,y1=box;ref=ec if label=='top_retained_gray' else a;c=ref[y0:y1,x0:x1];r=b[y0:y1,x0:x1];faces.append({'region':label,'box':box,'meanDeltaRGB':(r-c).mean((0,1)).tolist(),'originalStdRGB':c.std((0,1)).tolist(),'rawStdRGB':r.std((0,1)).tolist()})
qarefs=[]
for p in sorted(OUT.glob('qa-*.png')):
 qarefs.append(info(p));write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(OUT/'native.png'),info(OUT/'original-context.png'),info(OUT/'context.png')],'operation':'Native-pixel crops/juxtaposition or hard original context return for QA only','newModelCalls':0,'resampling':False})
write('comparison.json',{'native':info(OUT/'native.png'),'originalContext':info(OUT/'original-context.png'),'editContext':info(OUT/'context.png'),'regions':regions,'distinctContourMeasurements':measure,'faces':faces,'qa':qarefs,'registrationApplied':False,'blendingApplied':False,'joinedIntoCurrent':False,'caveat':'Distinct sign/structure peaks are measured; visual verification required. Left contour can leave its search window at lower rows.'})
print(json.dumps({'native':info(OUT/'native.png'),'regions':regions,'measurements':measure,'faces':faces},ensure_ascii=False))

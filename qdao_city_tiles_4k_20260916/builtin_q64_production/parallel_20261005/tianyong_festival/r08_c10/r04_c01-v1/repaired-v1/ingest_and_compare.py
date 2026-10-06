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
ctx=Image.open(OUT/'original-context.png').convert('RGB');a=np.asarray(ctx,dtype=float);b=np.asarray(native,dtype=float)
known=np.asarray(Image.open(OUT/'original-context.png'))[:,:,3]==255
regions={'left115':[0,0,115,1139],'right230':[1024,0,1254,1139],'bottom115':[0,1139,1254,1254]}
comparisons=[]
for key,box in regions.items():
    x0,y0,x1,y1=box;d=np.abs(a[y0:y1,x0:x1]-b[y0:y1,x0:x1])
    comparisons.append({'region':key,'box':box,'meanAbsRGB':d.mean((0,1)).tolist(),'maxAbsRGB':d.max((0,1)).tolist(),'pixelCount':(x1-x0)*(y1-y0),'exactEqualPixels':int(np.all(d==0,axis=2).sum())})
hard=b.copy();hard[known]=a[known]
Image.fromarray(hard.astype(np.uint8)).save(OUT/'qa-hard-context-return.png')
qa={
 'qa-bottom-original-above-raw-below.png':np.concatenate([a[1139:],b[1139:]],axis=0),
 'qa-left-original-beside-raw.png':np.concatenate([a[:1139,:115],b[:1139,:115]],axis=1),
 'qa-right-original-beside-raw.png':np.concatenate([a[:1139,1024:],b[:1139,1024:]],axis=1),
 'qa-hard-bottom-y1139.png':hard[1011:1254],
 'qa-hard-left-x115.png':hard[:1139,:243],
 'qa-hard-right-x1024.png':hard[:1139,896:],
}
for name,pixels in qa.items():Image.fromarray(pixels.astype(np.uint8)).save(OUT/name)
lum=lambda v:v@np.array([.2126,.7152,.0722])
al=lum(a);bl=lum(b);measure=[]
for y in [1143,1180,1220,1249]:
    aa=np.diff(al[max(1139,y-3):min(1254,y+4)].mean(0));bb=np.diff(bl[max(1139,y-3):min(1254,y+4)].mean(0))
    for lo,hi in [(1,115),(150,350),(650,910),(900,1100)]:
        e=lo+int(np.argmax(np.abs(aa[lo:hi])));l=max(lo,e-50);h=min(hi,e+51);r=l+int(np.argmax(np.sign(aa[e])*bb[l:h]))
        measure.append({'side':'bottom','y':y,'xSearchRange':[lo,hi],'contextEdge':e,'rawSamePolarityEdge':r,'offsetPx':r-e,'contextGradient':float(aa[e]),'rawGradient':float(bb[r])})
for x in [55,111,1027,1075,1180]:
    aa=np.diff(al[:1139,max(0,x-3):min(1254,x+4)].mean(1));bb=np.diff(bl[:1139,max(0,x-3):min(1254,x+4)].mean(1))
    ranges=[(90,230),(850,1040)] if x<115 else [(320,510),(710,1020)]
    for lo,hi in ranges:
        e=lo+int(np.argmax(np.abs(aa[lo:hi])));l=max(lo,e-50);h=min(hi,e+51);r=l+int(np.argmax(np.sign(aa[e])*bb[l:h]))
        measure.append({'side':'left' if x<115 else 'right','x':x,'ySearchRange':[lo,hi],'contextEdge':e,'rawSamePolarityEdge':r,'offsetPx':r-e,'contextGradient':float(aa[e]),'rawGradient':float(bb[r])})
qarefs=[]
for p in sorted(OUT.glob('qa-*.png')):
    qarefs.append(info(p));write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(OUT/'native.png'),info(OUT/'original-context.png')] if p.name!='qa-source-bottom-left230.png' else [info(OUT/'original-context.png')],'operation':'Native1:1 crop/juxtaposition or hard context return for seam diagnosis only; not accepted artwork','newModelCalls':0,'resampling':False})
write('comparison.json',{'native':info(OUT/'native.png'),'context':info(OUT/'original-context.png'),'knownPixels':int(known.sum()),'regions':comparisons,'contourMeasurements':measure,'measurementCaveat':'Same-polarity strongest edge can select a different bevel subedge; numeric samples support native visual inspection and are not automatic acceptance.','qa':qarefs,'resampling':False,'registrationApplied':False,'blendingApplied':False,'joinedIntoCurrent':False})
print(json.dumps({'native':info(OUT/'native.png'),'regions':comparisons,'contourMeasurements':measure},ensure_ascii=False))

from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def png(n,a):Image.fromarray(np.rint(a).clip(0,255).astype('uint8')).save(O/n)
receipt=read(O/'tool-response.json');host=Path(receipt['hostPath']);assert not (O/'native.png').exists()
with Image.open(host) as im:im.verify()
shutil.copy2(host,O/'native.png');assert sha(host)==sha(O/'native.png')
with Image.open(O/'native.png') as im:
 assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255)
 raw=np.asarray(im.convert('RGB'),np.float32)
req=read(O/'request.json');prep=read(O/'preparation.json')
write('native.png.generation.json',{'file':str(O/'native.png'),'sha256':sha(O/'native.png'),'generatedAt':None,'observedCompletionAt':receipt['hostObservedFinishedAtUtc'],'recordSavedAtUtc':datetime.now(timezone.utc).isoformat(),'timestampSemantics':'Server time unknown; host observation separate','width':1254,'height':1254,'route':'builtin','tool':'image_gen.imagegen','configSnapshot':req['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'No selector or verifiable model/quality return metadata','prompt':info(O/'prompt.txt'),'references':prep['references'],'globalCropLTRB':req['globalCropLTRB'],'tileLocalCropLTRB':req['tileLocalCropLTRB'],'evidence':{'actualRequest':info(O/'request.json'),'actualToolResponse':info(O/'tool-response.json'),'hostSavedOutput':str(host),'hostOutputSha256':sha(host),'copiedByteIdentically':True},'resizedAfterGeneration':False,'upscaled':False,'formalAccepted':False})
ctx=np.asarray(Image.open(O/'original-context.png').convert('RGBA'));known=ctx[:,:,3]==255;original=ctx[:,:,:3].astype(np.float32);hard=raw.copy();hard[known]=original[known]
png('qa-hard-native-return.png',hard);png('qa-bottom-original-above-raw-below.png',np.concatenate([original[1024:],raw[1024:]],0));png('qa-hard-bottom.png',hard[896:]);png('qa-hard-left.png',hard[:1024,:260]);png('qa-hard-right.png',hard[:1024,896:]);png('qa-bottom-corners.png',np.concatenate([hard[920:,:320],hard[920:,934:]],1))
stats=[]
for label,b in [('left',[0,0,115,1024]),('right',[1024,0,1254,1024]),('bottom',[0,1024,1254,1254]),('gray-plane',[680,1040,950,1120]),('ivory-band',[520,1040,550,1120])]:
 x0,y0,x1,y1=b;d=raw[y0:y1,x0:x1]-original[y0:y1,x0:x1];stats.append({'region':label,'box':b,'meanDeltaRGB':d.mean((0,1)).tolist(),'meanAbsRGB':np.abs(d).mean((0,1)).tolist(),'maxAbsRGB':np.abs(d).max((0,1)).tolist()})
lum=lambda a:a@np.array([.2126,.7152,.0722]);a=lum(original);b=lum(raw);profiles=[]
# Match whole signed gradient neighborhoods, preserving bevel+highlight identity.
for y in [1024,1032,1060,1090,1120,1160]:
 aa=np.diff(a[max(1024,y-3):y+4].mean(0));bb=np.diff(b[max(1024,y-3):y+4].mean(0))
 for lo,hi,label in [(350,450,'left ivory panel outer contour'),(440,510,'curve left border'),(570,655,'curve right bevel'),(975,1035,'gray right border')]:
  center=lo+int(np.argmax(np.abs(aa[lo:hi])));q=aa[center-15:center+16];loss=[]
  for dx in range(-32,33):
   s=bb[center-15+dx:center+16+dx];loss.append(float(np.mean((q-s)**2)))
  dx=int(np.argmin(loss))-32;profiles.append({'y':y,'edge':label,'originalGradientAnchorX':center,'rawMatchingDx':dx,'meanSquaredGradientError':min(loss)})
write('comparison.json',{'native':info(O/'native.png'),'sourceContext':info(O/'original-context.png'),'nativeRegionStats':stats,'gradientProfileMatches':profiles,'caveat':'Correspondence estimates only; visual actual-pixel check required; no automatic acceptance','geometryApplied':False,'joinedIntoCurrent':False})
for p in O.glob('qa-*.png'):
 write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(O/'native.png'),info(O/'original-context.png')],'operation':'Native-pixel hard-return diagnostic/crop, no resizing','newModelCalls':0,'formalAccepted':False})
print(json.dumps({'native':info(O/'native.png'),'profiles':profiles,'stats':stats},ensure_ascii=False))

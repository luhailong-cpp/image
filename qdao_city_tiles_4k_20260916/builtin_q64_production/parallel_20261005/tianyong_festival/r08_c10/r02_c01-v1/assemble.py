from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
P=Path(__file__).resolve().parent;T=P.parent.parent;O=P/'final-v1';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def png(n,a):Image.fromarray(np.rint(a).clip(0,255).astype('uint8')).save(O/n)
smooth=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
cpfile=T/'source-checkpoint.json';cpstart=sha(cpfile);cp=read(cpfile)
fr=cp['fragment'];lr=cp['coupledNeighbors']['r08_c09']
for r in [fr,lr]:assert sha(r['file'])==r['sha256']
context=Image.new('RGBA',(1254,1254));context.paste(Image.open(lr['file']).convert('RGBA').crop((3981,909,4096,2163)),(0,0));context.paste(Image.open(fr['file']).convert('RGBA').crop((0,909,1139,2163)),(115,0))
ctx=np.array(context);known=ctx[:,:,3]==255
expected=np.ones((1254,1254),bool);expected[230:1024,115:1024]=False;assert np.array_equal(known,expected)
assert np.array_equal(np.asarray(Image.open(P/'context-latest.png').convert('RGBA')),ctx),'Latest prospective differs from root context; inspect before assembly'
context.save(P/'context-current.png')
save('context-current-source.json',{'file':str(P/'context-current.png'),'sha256':sha(P/'context-current.png'),'sourceCheckpoint':info(cpfile),'sourceFiles':[fr,lr],'operation':'Exact actual committed native context; matches prospective final-v2 bit for bit','newModelCalls':0})
raw=np.array(Image.open(P/'lower-repair-v2/native.png').convert('RGB'));source=ctx[:,:,:3]
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# Explicit measured correction only. Whole strip contours were truly AI redrawn.
# Top gray/ivory bevel measured -1..-2px, bottom left -1px and right +1px, crossbar +1px.
top=-1.5*smooth((xx-450)/220)*(1-smooth((yy-230)/400))
bottom=np.interp(xx,[0,280,400,550,750,900,980,1090,1253],[0,0,0,-1,0,0,1,0,0]).astype(np.float32)*smooth((yy-780)/244)
dx=top+bottom
dy=smooth((xx-780)/244)*(1-smooth((xx-1080)/174))*smooth((yy-390)/180)*(1-smooth((yy-850)/200))
aligned=cv2.remap(raw,xx+dx,yy+dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
distance=cv2.distanceTransform((~known).astype('uint8'),cv2.DIST_L2,5)
delta=source.astype('float32')-aligned.astype('float32');delta[~known]=0
norm=cv2.GaussianBlur(known.astype('float32'),(0,0),24)
tone=cv2.GaussianBlur(delta,(0,0),24)/np.maximum(norm[:,:,None],.0001)
tone=np.clip(tone,-12,12)*(1-smooth(distance/220))[:,:,None]
corrected=np.clip(aligned.astype('float32')+tone,0,255)
alpha=smooth((xx-12)/103)*smooth((1154-xx)/130)*smooth((yy-60)/170)*smooth((1164-yy)/140)
alpha[~known]=1
joined=np.rint(corrected*alpha[:,:,None]+source.astype('float32')*(1-alpha[:,:,None])).clip(0,255).astype('uint8')
png('joined.png',joined);png('mask.png',alpha*255);np.save(O/'dx.npy',dx);np.save(O/'dy.npy',dy);np.save(O/'tone.npy',tone)
assert np.array_equal(joined[alpha==0],source[alpha==0])
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'output':info(O/'joined.png'),'derivedFrom':[info(P/'lower-repair-v2/native.png'),info(P/'context-current.png')],'operation':'Native1:1 composite after true AI structural redraw; explicit bounded cubic registration and local capped tone correction only. No enlargement, guide pixels or synthesized structure.','nativeScale':1,'maxDx':float(np.abs(dx).max()),'maxDy':float(np.abs(dy).max()),'maxToneRGB':np.abs(tone).max((0,1)).tolist(),'registrationBasis':info(P/'edge-measurements.json'),'resampling':'OpenCV cubic only within bounded displacement; output size unchanged','fields':[info(O/n) for n in ['mask.png','dx.npy','dy.npy','tone.npy']],'script':info(Path(__file__)),'formalAccepted':False}
save('assembly.json',record);save('joined.png.generation.json',{**info(O/'joined.png'),'derivedFrom':record['derivedFrom'],'operation':record['operation'],'nativeScale':1,'newModelCalls':0,'assembly':info(O/'assembly.json')})
save('mask.png.generation.json',{**info(O/'mask.png'),'derivedFrom':[info(P/'context-current.png')],'operation':'Compositing weight only, not game artwork','assembly':info(O/'assembly.json'),'newModelCalls':0})
for n,b in [('top.png',[0,0,1254,420]),('bottom.png',[0,820,1254,1254]),('left.png',[0,0,410,1254]),('right.png',[834,0,1254,1254])]:
 Image.fromarray(joined).crop(b).save(O/n);save(n+'.generation.json',{**info(O/n),'derivedFrom':[info(O/'joined.png')],'operation':'Exact native visual QA crop','cropLTRB':b,'newModelCalls':0})
assert sha(cpfile)==cpstart
print(json.dumps(record))

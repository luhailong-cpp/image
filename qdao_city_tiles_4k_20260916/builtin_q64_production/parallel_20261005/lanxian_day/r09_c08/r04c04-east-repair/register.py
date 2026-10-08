from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day').resolve()
D=ROOT/'r09_c08/r04c04-east-repair'; OUT=D/'registered-v1'; OUT.mkdir(exist_ok=True)
assert OUT.resolve().is_relative_to(ROOT)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)
def smooth(t): t=np.clip(t,0,1); return t*t*(3-2*t)
op=D/'original/native/r04_c04.png'; ap=D/'ai-attempt01/native/r04_c04.png'; ep=ROOT/'r09_c09/selected/extended4326.png'
orig=read(op); ai=read(ap); east=read(ep)[3072:4326,0:230]
def centers(a):
 gray=a.mean(2); cs=[]; widths=[]
 for x in range(a.shape[1]):
  rows=np.where(gray[20:360,x]<160)[0]+20
  assert len(rows)>0
  cs.append((rows[0]+rows[-1])/2); widths.append(rows[-1]-rows[0]+1)
 return np.array(cs),np.array(widths)
oc,ow=centers(orig); ac,aw=centers(ai); ec,ew=centers(east)
x=np.arange(1254,dtype=float); Y,X=np.mgrid[0:1254,0:1254]
x0=640.; x1=1139.; L=x1-x0
leftfit=np.polyfit(x[550:730],oc[550:730],2); y0=float(np.polyval(leftfit,x0)); m0=float(np.polyval(np.polyder(leftfit),x0))
rightfit=np.polyfit(np.arange(115,200)-115,ec[115:200],1); y1=float(np.polyval(rightfit,0)); m1=float(rightfit[0])
t=np.clip((x-x0)/L,0,1)
target=(2*t**3-3*t**2+1)*y0+(t**3-2*t**2+t)*L*m0+(-2*t**3+3*t**2)*y1+(t**3-t**2)*L*m1
sourcefit=np.polyfit(x[580:1254],ac[580:1254],4); source=np.polyval(sourcefit,x)
targetwidth= float(np.median(ow[600:700]))*(1-smooth(t))+float(np.median(ew[115:180]))*smooth(t)
sourcewidth=np.clip(np.polyval(np.polyfit(x[580:1254],aw[580:1254],2),x),5,20)
scale=np.clip(targetwidth/sourcewidth,.8,1.6)
near=np.abs(Y-target[None,:]); ygain=1-smooth((near-35)/40)
xgain=smooth((X-640)/140); mask=xgain*ygain
mask[(X>=1139)|(Y<115)]=0
mapY=Y+((source[None,:]+(Y-target[None,:])/scale[None,:])-Y)*ygain
mapY=np.clip(mapY,0,1253)
lo=np.floor(mapY).astype(int); hi=np.minimum(lo+1,1253); frac=mapY-lo
sample=ai[lo,X]*(1-frac[:,:,None])+ai[hi,X]*frac[:,:,None]
result=np.rint(orig*(1-mask[:,:,None])+sample*mask[:,:,None]).clip(0,255).astype(np.uint8)
result[115:,1139:]=east[115:,115:].astype(np.uint8)
assert np.array_equal(result[:115],orig[:115].astype(np.uint8))
assert np.array_equal(result[115:,1139:],east[115:,115:].astype(np.uint8))
assert np.array_equal(result[:,0:640],orig[:,0:640].astype(np.uint8))
Image.fromarray(result).save(OUT/'candidate1254.png')
Image.fromarray(np.rint(mask*255).astype(np.uint8)).save(OUT/'ai-patch-mask.png')
np.savez_compressed(OUT/'registration-fields.npz',destinationToSourceDy=(mapY-Y).astype(np.float32),blendMask=mask.astype(np.float32),targetCenter=target.astype(np.float32),sourceCenter=source.astype(np.float32),verticalScale=scale.astype(np.float32))
changed=np.any(result!=orig.astype(np.uint8),axis=2); core=changed[115:1139,115:1139]; ys,xs=np.where(core)
maxdy=float(np.max(np.abs((mapY-Y)[mask>0])))
record={'createdAt':datetime.now(timezone.utc).isoformat(),'candidatePath':str(OUT/'candidate1254.png'),'candidateSha256':sha(OUT/'candidate1254.png'),'sources':[{'path':str(p),'sha256':sha(p)} for p in [op,ap,ep]],'aiGenerationRecord':str(Path(str(ap)+'.generation.json')),'operation':'Use native AI-repainted groove only in bounded local mask. Vertical coordinate registration by cubic Hermite target center and smoothly changing native channel thickness. One bilinear coordinate sampling; no blur/convolution/unsharp. Blend native AI into original only in quiet skirt around existing groove; original retained outside mask. Exact eastern neighbor right115 restored below top115.','limits':{'xRangeForCoreEditing':[640,1139],'coreChangedNativeBounds':[int(xs.min()+115),int(ys.min()+115),int(xs.max()+116),int(ys.max()+116)],'top115Unchanged':True,'left640Unchanged':True,'right115ExactNeighbor':True,'coreChangedPixelCount':int(core.sum()),'maximumDyPixels':maxdy,'verticalScaleRange': [float(scale[640:1139].min()),float(scale[640:1139].max())]},'hermite':{'x0':x0,'x1':x1,'startY':y0,'startSlope':m0,'endY':y1,'endSlope':m1},'fieldPath':str(OUT/'registration-fields.npz'),'fieldSha256':sha(OUT/'registration-fields.npz'),'maskPath':str(OUT/'ai-patch-mask.png'),'maskSha256':sha(OUT/'ai-patch-mask.png'),'status':'Pending actual view; not ingested and not accepted','actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None}
(OUT/'processing.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Exact QA boards, no resampling
imgs={}
eastcore=Image.open(ROOT/'r09_c09/selected/core4096.png').convert('RGB'); candidate=Image.fromarray(result)
b=Image.new('RGB',(512,1024)); b.paste(candidate.crop((883,115,1139,1139))); b.paste(eastcore.crop((0,3072,256,4096)),(256,0)); imgs['east-row4']=b
imgs['guide-x3981']=candidate.crop((960,115,1088,1139))
imgs['patch-entry-x640']=candidate.crop((576,115,704,400)); imgs['patch-entry-x780']=candidate.crop((716,115,844,400))
imgs['patch-full']=candidate.crop((576,115,1254,400))
imgs['patch-outer-bottom']=candidate.crop((576,300,1254,420))
north=Image.open(ROOT/'r09_c08/native/r03_c04.png').convert('RGB')
b=Image.new('RGB',(1024,256)); b.paste(north.crop((115,1011,1139,1139))); b.paste(candidate.crop((115,115,1139,243)),(0,128)); imgs['internal-y3072']=b
imgs['guide-y3187']=candidate.crop((115,166,1139,294))
q=[]
for name,im in imgs.items():
 p=OUT/(name+'.png'); im.save(p); q.append({'id':name,'path':str(p),'sha256':sha(p),'rgbSha256':hashlib.sha256(im.tobytes()).hexdigest(),'width':im.width,'height':im.height,'actualViewCompleted':False})
(OUT/'qa-export.json').write_text(json.dumps({'candidateSha256':record['candidateSha256'],'count':len(q),'boards':q},indent=2)+'\n',encoding='utf-8')
print(json.dumps(record['limits'],indent=2))

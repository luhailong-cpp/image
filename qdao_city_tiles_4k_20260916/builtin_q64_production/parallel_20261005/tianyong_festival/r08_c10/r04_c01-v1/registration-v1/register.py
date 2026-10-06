from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
OUT=Path(__file__).resolve().parent;PIECE=OUT.parent;SRC=PIECE/'shifted-curve-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
    with (OUT/n).open('x',encoding='utf-8') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
def png(n,a):Image.fromarray(np.clip(np.rint(a),0,255).astype('uint8')).save(OUT/n)
def ss(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
def fit(y,v):
    yy=(np.asarray(y)-627)/128;vv=np.asarray(v);keep=np.ones(len(y),bool)
    for _ in range(8):
        p=np.polynomial.polynomial.polyfit(yy[keep],vv[keep],2);err=vv-np.polynomial.polynomial.polyval(yy,p)
        kk=np.abs(err)<=max(1.5,3*np.median(np.abs(err[keep]-np.median(err[keep]))))
        if np.array_equal(keep,kk):break
        assert kk.sum()>len(y)*.6;keep=kk
    return p,keep
def ev(p,y):return np.polynomial.polynomial.polyval((np.asarray(y)-627)/128,p)
assert sha(SRC/'native.png')=='de247dbb4b9ae0828d6881f5eb30ca234508649ce3920919e429f6bcedeb66ae'
raw=np.asarray(Image.open(SRC/'native.png').convert('RGB'),np.float32)
ctx=np.asarray(Image.open(SRC/'original-context.png').convert('RGB'),np.float32)
known=np.asarray(Image.open(SRC/'original-context.png'))[:,:,3]==255
lum=lambda a:a@np.array([.2126,.7152,.0722]);gl=lum(raw);cl=lum(ctx)
ys=np.arange(630,752,4);records=[];txs=[];dxs=[];leftt=[];leftd=[]
for y in ys:
    a=np.diff(cl[y-3:y+4].mean(0));b=np.diff(gl[y-3:y+4].mean(0))
    w=650+int(np.argmax(a[650:930]));g=w-65+int(np.argmax(-a[w-65:w-25]))
    rw=w-35+int(np.argmax(b[w-35:w+36]));rg=g-35+int(np.argmax(-b[g-35:g+36]))
    le=100+int(np.argmax(-a[100:260]));lr=max(80,le-12)+int(np.argmax(-b[max(80,le-12):le+13]))
    txs.append(w);dxs.append(((rw-w)+(rg-g))/2);leftt.append(le);leftd.append(lr-le)
    records.append({'y':int(y),'rightGrayDarkTarget':g,'rightGrayDarkRaw':rg,'rightBrightTarget':w,'rightBrightRaw':rw,'targetBevelWidth':w-g,'rawBevelWidth':rw-rg,'rightPairMeanDx':dxs[-1],'leftTarget':le,'leftRaw':lr})
pt,kt=fit(ys,txs);pd,kd=fit(ys,dxs);plt,klt=fit(ys,leftt);pld,kld=fit(ys,leftd)
flow=np.zeros((1254,1254,2),np.float32);xx=np.arange(1254,dtype=float)
for y in range(1254):
    # Both existing right contours move together;45px bevel thickness is retained.
    center=float(ev(pt,y if y>=627 else max(y,300)))
    center=float(np.clip(center,1,1252))
    if y<450:
        dtop=float(np.clip(pd[0]-pd[1]/128*177,-24,24));d=dtop*float(ss((y-128)/322))
    elif y<627:
        d0=float(pd[0]);slope=float(pd[1]/128);dtop=float(np.clip(d0-slope*177,-24,24));t=(y-450)/177
        d=(2*t**3-3*t*t+1)*dtop+(-2*t**3+3*t*t)*d0+(t**3-t*t)*177*slope
    else:d=float(ev(pd,min(y,751)))*float(1-ss((y-723)/128))
    d=float(np.clip(d,-24,24))
    profile=ss((xx-(center-300))/240)*(1-ss((xx-(center+10))/165))
    flow[y,:,0]+=d*profile
    lc=float(ev(plt,max(627,min(y,751))))
    ld=float(ev(pld,max(627,min(y,751))))
    ld*=float(ss((y-400)/227)) if y<627 else float(1-ss((y-723)/128))
    lprof=ss((xx-(lc-80))/60)*(1-ss((xx-(lc+20))/100))
    flow[y,:,0]+=ld*lprof
assert np.max(np.abs(flow))<=24 and np.count_nonzero(flow[:,:,1])==0
mx,my=np.meshgrid(np.arange(1254,dtype=np.float32),np.arange(1254,dtype=np.float32))
aligned=cv2.remap(raw,mx+flow[:,:,0],my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# Original-source low-frequency tone, bounded12/channel, no missing reference pixels.
grad=np.abs(np.diff(cl,axis=1,append=cl[:,-1:])).astype('float32')
quiet=(cv2.GaussianBlur(grad,(0,0),3)<2).astype('float32')*known
den=cv2.GaussianBlur(quiet,(0,0),32)
delta=ctx-aligned
tone=np.stack([cv2.GaussianBlur(delta[:,:,c]*quiet,(0,0),32)/np.maximum(den,1e-6) for c in range(3)],2)
tone=np.clip(tone,-12,12).astype('float32')
# Spread lower measured tone into genuinely missing interior continuously.
for y in range(627):
    t=float(ss((y-250)/377));interior=~known[y];tone[y,interior]=tone[627,interior]*t
corrected=np.clip(aligned+tone,0,255)
ax=ss((np.arange(1254)-51)/64)*(1-ss((np.arange(1254)-1024)/64))
ay=1-ss((np.arange(1254)-627)/96)
alpha=np.minimum(ax[None,:],ay[:,None]);alpha[~known]=1
shiftjoined=corrected*alpha[:,:,None]+ctx*(1-alpha[:,:,None])
shiftjoined=np.rint(shiftjoined).clip(0,255).astype('uint8')
assert np.array_equal(shiftjoined[723:],ctx[723:].astype('uint8'))
png('shifted-aligned.png',aligned);png('shifted-joined.png',shiftjoined)
np.save(OUT/'flow.npy',flow);np.save(OUT/'tone.npy',tone);np.save(OUT/'blend-alpha.npy',alpha.astype('float32'))
png('blend-mask.png',alpha*255)

# Assemble exact old r04_c01 world window from warm upper and shifted lower native art.
upper=np.asarray(Image.open(PIECE/'repaired-v1/native.png').convert('RGB'),np.float32)
oldctx=np.asarray(Image.open(PIECE/'repaired-v1/original-context.png').convert('RGB'),np.float32)
oldknown=np.asarray(Image.open(PIECE/'repaired-v1/original-context.png'))[:,:,3]==255
assembly=upper.copy();assembly[512:]=shiftjoined[:742]
for k in range(128):
    w=float(ss(k/127));assembly[512+k]=upper[512+k]*(1-w)+shiftjoined[k]*w
# Maintain original outer context, blend the existing upper candidate in native strips.
for y in range(512):
    a=ax.copy();a[~oldknown[y]]=1;assembly[y]=assembly[y]*a[:,None]+oldctx[y]*(1-a[:,None])
png('joined-r04_c01.png',assembly)
joined=np.asarray(Image.open(OUT/'joined-r04_c01.png'))
png('qa-bottom-original-above-aligned-below.png',np.concatenate([ctx[627:723],aligned[627:723]],0))
png('qa-shifted-return-y627.png',shiftjoined[499:755])
png('qa-old-upper-join-y512.png',joined[384:768])
png('qa-old-bottom-y1139.png',joined[1011:1254])
png('qa-old-left-x115.png',joined[:1139,:243]);png('qa-old-right-x1024.png',joined[:1139,896:])
measure=[]
for y in [627,631,650,675,700,720]:
    a=np.diff(cl[max(627,y-3):y+4].mean(0));b=np.diff(lum(aligned[max(627,y-3):y+4]).mean(0));j=np.diff(lum(shiftjoined[max(627,y-3):y+4]).mean(0))
    w=650+int(np.argmax(a[650:930]));g=w-65+int(np.argmax(-a[w-65:w-25]));le=100+int(np.argmax(-a[100:260]))
    for label,e,pol in [('right_gray_to_dark',g,-1),('right_dark_to_ivory',w,1),('left',le,-1)]:
        r=e-5+int(np.argmax(pol*b[e-5:e+6]));q=e-5+int(np.argmax(pol*j[e-5:e+6]));measure.append({'y':y,'edge':label,'originalX':e,'alignedX':r,'joinedX':q,'alignedResidual':r-e,'joinedResidual':q-e})
write('parameters.json',{'method':'Existing paired-contour-guided horizontal inverse remap after AI material/structure repairs; no missing geometry added','maxAllowedDisplacement':24,'actualMaxAbsXY':[float(np.max(np.abs(flow[:,:,i]))) for i in range(2)],'flowBoundary627MaxRowStep':float(np.max(np.abs(flow[627]-flow[626]))),'minimumHorizontalJacobian':float(np.min(1+np.diff(flow[:,:,0],axis=1))),'rightTargetPolynomial':pt.tolist(),'rightDxPolynomial':pd.tolist(),'leftTargetPolynomial':plt.tolist(),'leftDxPolynomial':pld.tolist(),'polynomialY':'(y-627)/128','fitRows':ys.tolist(),'measurements':records,'rightXProfile':'C1 smoothstep rise from contourX-300 to-60; plateau through+10, fall to+175','unknownYExtension':'C1 ramp128..450; Hermite450..627 matching known endpoint derivative; not zero at unknown boundary','knownFadeY':[723,851],'toneMaxAllowed':12,'actualToneMaxRGB':[float(np.max(np.abs(tone[:,:,i]))) for i in range(3)],'toneEstimator':'quiet known original samples, normalized Gaussian32; missing interior receives continuous lower anchor','blend':'left known51..115 and right1024..1088; lower627..723; smoothstep','composition':'warm repair old y0..512 plus shifted first742 rows at old y512,128px overlap blend','resampling':'native-sized INTER_CUBIC for bounded displacement only; no global scale/rotation','sourceNative':info(SRC/'native.png'),'sourceContext':info(SRC/'original-context.png'),'upperSource':info(PIECE/'repaired-v1/native.png'),'sourceDimensions':[1254,1254],'outputDimensions':[1254,1254],'originalTileLocalLTRB':[-115,2957,1139,4211],'originalGlobalLTRB':[36749,31629,38003,32883],'shiftedTileLocalLTRB':[-115,3469,1139,4723],'joinedIntoCurrent':False,'accepted':False})
write('measurements.json',{'contourResiduals':measure,'maxAbsAlignedResidual':max(abs(m['alignedResidual']) for m in measure),'maxAbsJoinedResidual':max(abs(m['joinedResidual']) for m in measure),'exactOriginalAfterShiftY723':bool(np.array_equal(shiftjoined[723:],ctx[723:].astype('uint8'))),'exactOriginalAfterOldY1235':bool(np.array_equal(joined[1235:],oldctx[1235:].astype('uint8'))),'sourceBytesUntouched':True,'accepted':False})
for p in sorted(OUT.glob('*.png')):
    write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedAtUtc':datetime.now(timezone.utc).isoformat(),'generatedAt':None,'newModelCalls':0,'operation':'Mechanical bounded registration, native composition or QA; no new AI pixels','sourceGenerations':[info(SRC/'native.png.generation.json'),info(PIECE/'repaired-v1/native.png.generation.json')],'parameters':info(OUT/'parameters.json'),'flow':info(OUT/'flow.npy'),'tone':info(OUT/'tone.npy'),'alpha':info(OUT/'blend-alpha.npy'),'actualModel':None,'actualQuality':None,'formalAccepted':False,'pendingVisualReview':True})
print(json.dumps({'joined':info(OUT/'joined-r04_c01.png'),'maxFlow':float(np.abs(flow).max()),'maxTone':float(np.abs(tone).max()),'maxResidual':max(abs(m['joinedResidual']) for m in measure),'residuals':measure},ensure_ascii=False))

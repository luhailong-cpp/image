from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')))
import cv2

OUT = Path(__file__).resolve().parent
SRC = OUT.parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
info = lambda p: {'file': str(Path(p).resolve()), 'sha256': sha(p)}
def write(name, obj):
    with (OUT / name).open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2); f.write('\n')
def png(name, arr):
    path = OUT / name
    assert not path.exists(), name
    Image.fromarray(np.clip(np.rint(arr), 0, 255).astype(np.uint8)).save(path)
def smooth(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)
def robust_fit(y, v):
    yy = (np.asarray(y)-627)/128
    vv = np.asarray(v, dtype=float)
    use = np.ones(len(y), dtype=bool)
    for _ in range(8):
        p = np.polynomial.polynomial.polyfit(yy[use], vv[use], 2)
        resid = vv - np.polynomial.polynomial.polyval(yy, p)
        new = np.abs(resid) <= max(1.5, 3*np.median(np.abs(resid[use]-np.median(resid[use]))))
        if np.array_equal(new, use): break
        assert new.sum() >= len(y)//2
        use = new
    return p, use
def val(p, y): return np.polynomial.polynomial.polyval((np.asarray(y)-627)/128, p)

assert sha(SRC/'native.png') == '87cb716a838c5b1a784f30785b1457107c5e25f30d45402d06e791994253d83c'
assert sha(SRC/'context.png') == 'e25a429c402e081d865433dbbc4695cce307585a287f9caced8311084dfe399b'
raw = np.asarray(Image.open(SRC/'native.png').convert('RGB'), dtype=np.float32)
ctx = np.asarray(Image.open(SRC/'context.png').convert('RGB'), dtype=np.float32)
assert raw.shape == ctx.shape == (1254,1254,3)
N=1254
lum = lambda a: a @ np.array([.2126,.7152,.0722])
gl = lum(raw); cl = lum(ctx)
windows = [(70,180),(330,450),(450,570),(700,815),(840,960),(1100,1240)]
ys = np.arange(630, 819, 4)
records=[]; target_tracks=[]; shift_tracks=[]; fit_records=[]
for track_id,(lo,hi) in enumerate(windows):
    tx=[]; rx=[]
    for y in ys:
        a=np.diff(cl[y-3:y+4].mean(0)); b=np.diff(gl[y-3:y+4].mean(0))
        e=lo+int(np.argmax(np.abs(a[lo:hi])))
        rl=max(lo,e-30); rh=min(hi,e+31)
        r=rl+int(np.argmax(np.sign(a[e])*b[rl:rh]))
        tx.append(e);rx.append(r)
    pt,ut=robust_fit(ys,tx)
    pd,ud=robust_fit(ys,np.array(rx)-tx)
    target_tracks.append(pt);shift_tracks.append(pd)
    fit_records.append({'track':track_id,'window':list((lo,hi)),'targetXPolynomial':pt.tolist(),'dxPolynomial':pd.tolist(),'polynomialYCoordinate':'(y-627)/128','fitDegree':2,'targetInlierCount':int(ut.sum()),'dxInlierCount':int(ud.sum()),'pointCount':len(ys),'targetDxAt627':float(pd[0]),'targetDxSlopeAt627':float(pd[1]/128),'maxDxResidualInliers':float(np.max(np.abs((np.array(rx)-tx-val(pd,ys))[ud])))})
    records += [{'track':track_id,'y':int(y),'targetX':int(t),'rawX':int(r),'dx':int(r-t),'targetFitInlier':bool(ut[i]),'dxFitInlier':bool(ud[i])} for i,(y,t,r) in enumerate(zip(ys,tx,rx))]

# Horizontal-only inverse map: target pixel (x,y) samples raw (x+dx,y).
# Six slab contours are already present; no contour is added or substituted.
flow=np.zeros((N,N,2),np.float32)
knots_by_y=np.zeros((N,8),np.float64)
dx_by_y=np.zeros((N,8),np.float64)
xx=np.arange(N,dtype=float)
for y in range(N):
    knot_y=max(627,min(y,819))
    knots=np.array([0]+[float(val(p,knot_y)) for p in target_tracks]+[N-1])
    d=[]
    for p in shift_tracks:
        d0=float(p[0]); slope=float(p[1]/128)
        top=float(np.clip(d0-slope*(627-395),-24,24))
        if y<395:
            z=top*float(smooth((y-250)/145))
        elif y<627:
            t=(y-395)/232
            z=(2*t**3-3*t*t+1)*top+(-2*t**3+3*t*t)*d0+(t**3-t*t)*232*slope
        else:
            z=float(val(p,min(y,819)))
            z*=float(1-smooth((y-755)/128))
        d.append(float(np.clip(z,-24,24)))
    values=np.array([0]+d+[0])
    for k in range(7):
        sel=(xx>=knots[k])&(xx<=knots[k+1])
        t=(xx[sel]-knots[k])/(knots[k+1]-knots[k])
        flow[y,sel,0]=values[k]+(values[k+1]-values[k])*smooth(t)
    knots_by_y[y]=knots;dx_by_y[y]=values
assert np.max(np.abs(flow)) <= 24
assert np.count_nonzero(flow[:,:,1])==0
mx,my=np.meshgrid(np.arange(N,dtype=np.float32),np.arange(N,dtype=np.float32))
aligned=cv2.remap(raw,mx+flow[:,:,0],my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)

# Low-frequency RGB offset computed from actual original native overlap only.
# Exclude strong gradients from the estimator; do not color-match across shapes.
grad=np.abs(np.diff(cl,axis=1,append=cl[:,-1:]))
quiet=(cv2.GaussianBlur(grad.astype(np.float32),(0,0),3)<2).astype(np.float32)
quiet[:627]=0;quiet[851:]=0
den=cv2.GaussianBlur(quiet,(0,0),40)
delta=ctx-aligned
tone0=np.stack([cv2.GaussianBlur(delta[:,:,c]*quiet,(0,0),40)/np.maximum(den,1e-6) for c in range(3)],axis=2)
tone=np.clip(tone0,-12,12)
anchor=tone[627].copy()
for y in range(627):
    tone[y]=anchor*float(smooth((y-250)/377))
tone[851:]=0
assert np.max(np.abs(tone))<=12
corrected=np.clip(aligned+tone,0,255)

# New upper627 plus a128px transition into original, exact originals from y755.
alpha=(1-smooth((np.arange(N)-627)/128)).astype(np.float32)
alpha[:627]=1;alpha[755:]=0
joined=corrected*alpha[:,None,None]+ctx*(1-alpha[:,None,None])
joined=np.clip(np.rint(joined),0,255).astype(np.uint8)
assert np.array_equal(joined[755:],ctx[755:].astype(np.uint8))
png('aligned.png',aligned)
png('tone-corrected.png',corrected)
png('joined.png',joined)
png('blend-mask.png',np.repeat((255*alpha)[:,None],N,axis=1))
np.save(OUT/'flow.npy',flow)
np.save(OUT/'tone.npy',tone.astype(np.float32))
np.save(OUT/'blend-alpha.npy',alpha)
np.save(OUT/'contour-knots.npy',knots_by_y)
np.save(OUT/'contour-shifts.npy',dx_by_y)

# Original-size inspection sheets: no rescaling or low-resolution guide pixels.
png('qa-return-y627.png',joined[499:755])
png('qa-return-y755.png',joined[627:883])
png('qa-upper-y395.png',joined[267:523])
png('qa-original-overlap-above-registered-below.png',np.concatenate([ctx[627:883],joined[627:883]],axis=0))
png('qa-original-above-aligned-below.png',np.concatenate([ctx[627:755],aligned[627:755]],axis=0))
png('qa-native-above-joined-below.png',np.concatenate([raw[395:755],joined[395:755]],axis=0))
flowrgb=np.zeros((N,N,3),np.float32)+127.5
flowrgb[:,:,0]+=flow[:,:,0]/24*127.5
flowrgb[:,:,2]-=flow[:,:,0]/24*127.5
png('qa-horizontal-flow.png',flowrgb)

residual=[]
for y in [627,631,650,675,700,725,750]:
    a=np.diff(cl[max(627,y-3):y+4].mean(0))
    b=np.diff(lum(aligned[max(627,y-3):y+4]).mean(0))
    j=np.diff(lum(joined[max(627,y-3):y+4]).mean(0))
    for i,p in enumerate(target_tracks):
        center=int(round(float(val(p,y))))
        lo=center-6;hi=center+7
        e=lo+int(np.argmax(np.abs(a[lo:hi])))
        r=lo+int(np.argmax(np.sign(a[e])*b[lo:hi]))
        q=lo+int(np.argmax(np.sign(a[e])*j[lo:hi]))
        residual.append({'y':y,'track':i,'targetX':e,'alignedX':r,'joinedX':q,'alignedMinusTargetX':r-e,'joinedMinusTargetX':q-e})

npix=N*128
diagnostic={
    'dimensions':[N,N], 'nativeScale':1, 'upscaled':False, 'newGenerationCalls':0,
    'sourceBytesUntouched':True, 'sourceNative':info(SRC/'native.png'), 'sourceContext':info(SRC/'context.png'),
    'flowMaxAbsXY':[float(np.max(np.abs(flow[:,:,i]))) for i in range(2)],
    'flowBoundary627MaxRowChange':float(np.max(np.abs(flow[627]-flow[626]))),
    'flowBoundary395MaxRowChange':float(np.max(np.abs(flow[395]-flow[394]))),
    'flowBoundary250MaxRowChange':float(np.max(np.abs(flow[250]-flow[249]))),
    'flowMaxRowChange':float(np.max(np.abs(np.diff(flow,axis=0)))),
    'flowMaxRowSecondDifference':float(np.max(np.abs(np.diff(flow,axis=0,n=2)))),
    'inverseMappingMinHorizontalJacobian':float(np.min(1+np.diff(flow[:,:,0],axis=1))),
    'toneMaxAbsRGB':[float(np.max(np.abs(tone[:,:,i]))) for i in range(3)],
    'toneAtBoundary627MaxRowChangeRGB':np.max(np.abs(tone[627]-tone[626]),axis=0).tolist(),
    'unchangedOriginalRegionLTRB':[0,755,N,N],
    'unchangedOriginalPixelCount':N*(N-755),
    'unchangedOriginalExact':bool(np.array_equal(joined[755:],ctx[755:].astype(np.uint8))),
    'unchangedUpperRegionLTRB':[0,0,N,251],
    'unchangedUpperExact':bool(np.array_equal(joined[:251],raw[:251].astype(np.uint8))),
    'overlapComparisonLTRB':[0,627,N,755],
    'overlapMeanAbsRGBBefore':np.abs(raw[627:755]-ctx[627:755]).mean((0,1)).tolist(),
    'overlapMeanAbsRGBAfterGeometry':np.abs(aligned[627:755]-ctx[627:755]).mean((0,1)).tolist(),
    'overlapMeanAbsRGBAfterGeometryTone':np.abs(corrected[627:755]-ctx[627:755]).mean((0,1)).tolist(),
    'measuredContourResiduals':residual,
    'maxAbsContourResidualAligned':max(abs(r['alignedMinusTargetX']) for r in residual),
    'maxAbsContourResidualJoined':max(abs(r['joinedMinusTargetX']) for r in residual),
    'joinedIntoCurrent':False,'formalAccepted':False,
}
write('measurements.json',diagnostic)
write('contour-fit.json',{'fitRecords':fit_records,'measurements':records,'notes':'Strongest same-polarity native edge used. Robust quadratic excludes contrast-driven bevel subedge switches. All six existing slab side edges matched one to one; visual confirmation required.'})
write('parameters.json',{
    'method':'Sparse existing-contour-guided horizontal inverse remap, bounded smooth field; no optical flow or generated pixels',
    'maximumDisplacementPx':24,'verticalDisplacementPx':0,'mapping':'output(x,y) samples native(x+dx,y)',
    'interpolation':'OpenCV INTER_CUBIC','border':'BORDER_REPLICATE; x-boundary displacement exactly zero',
    'targetContourWindows':windows,'fitRows':ys.tolist(),'robustFit':'degree2, iterative MAD rejection, minimum cutoff1.5px, normalized y=(y-627)/128',
    'xFieldInterpolation':'C1 cubic smoothstep between six target contour knots and zero-displacement image boundaries',
    'unknownExtension':{'zeroAboveY':250,'smoothRiseY':[250,395],'constantEndpointRule':'top displacement clip(dx627-slope627*232,-24,24)','hermiteY':[395,627],'hermiteUpperDerivative':0,'hermiteLowerDerivative':'fitted known contour dx derivative at627','notes':'Displacement continues through alpha boundary627; it is not zeroed at known/missing boundary. Upper fade is inside horizontal ivory cross-band, not mid-slab.'},
    'knownFieldFadeY':[755,883],'fadeIsAfterBlendEnds':True,
    'tone':{'maxAbsPerChannel':12,'estimator':'native context minus geometrically aligned generated image, normalized Gaussian sigma40, quiet-gradient samples only','sampleRegionY':[627,851],'quietGradientThreshold':2,'quietGradientBlurSigma':3,'unknownExtension':'anchor at627 times smoothstep((y-250)/377)','noLowResolutionGuidePixels':True},
    'blend':{'newWeightOneUntilY':627,'transitionY':[627,755],'curve':'1-smoothstep((y-627)/128)','exactOriginalFromY':755},
    'outputDimensions':[1254,1254],'globalCropLTRB':[37773,31002,39027,32256],'tileLocalCropLTRB':[909,2330,2163,3584],
    'newlyPaintedCoverageTileLocalLTRB':[909,2330,2163,2957],'transitionTileLocalLTRB':[909,2957,2163,3085],
    'exactOriginalCoverageTileLocalLTRB':[909,3085,2163,3584],
    'mechanicalOnly':True,'newModelCalls':0,'rootCurrentModified':False,
})
for name in ['aligned.png','tone-corrected.png','joined.png','blend-mask.png','qa-return-y627.png','qa-return-y755.png','qa-upper-y395.png','qa-original-overlap-above-registered-below.png','qa-original-above-aligned-below.png','qa-native-above-joined-below.png','qa-horizontal-flow.png']:
    write(name+'.generation.json',{'file':str(OUT/name),'sha256':sha(OUT/name),'generatedAt':None,'derivedAtUtc':datetime.now(timezone.utc).isoformat(),'derivation':'Mechanical registration/QA; no new AI generation','sourceGenerationRecord':info(SRC/'native.png.generation.json'),'nativeInput':info(SRC/'native.png'),'originalContext':info(SRC/'context.png'),'actualModel':None,'actualQuality':None,'newModelCalls':0,'nativeScale':1,'upscaled':False,'parameters':info(OUT/'parameters.json'),'script':info(Path(__file__)),'fieldFiles':[info(OUT/'flow.npy'),info(OUT/'tone.npy'),info(OUT/'blend-alpha.npy')],'accepted':False,'pendingVisualReview':True})
write('artifact-manifest.json',{'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'files':[info(p) for p in sorted(OUT.iterdir()) if p.is_file()]})
print(json.dumps({k:v for k,v in diagnostic.items() if k not in ['measuredContourResiduals']},ensure_ascii=False))

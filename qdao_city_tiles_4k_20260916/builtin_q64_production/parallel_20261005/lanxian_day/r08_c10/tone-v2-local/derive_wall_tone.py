"""RGB-only completion of the continuous wall-plane color join after saved geometry."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;T=O.parent;Q=O/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:{'file':str(p),'sha256':sha(p)}
ip=T/'combined-internal-v1/core4096.png';gp=T/'geometry-v2/core4096.png'
assert sha(ip)=='d0b672162e0daf6b0c829cbc0f4a482f5c95c2a50cd718bf61fee2bade8e14a1'
assert sha(gp)=='e3f8230a2e8f04790e9743d01ce07cb25008fd157136d47e67b8745221aacd2f'
src=np.array(Image.open(ip).convert('RGB'));geo=np.array(Image.open(gp).convert('RGB'))
a=src.astype(np.float32);previous=a-geo.astype(np.float32)
assert np.abs(previous).max()<=12
x0,x1,y0,y1,seam=2520,2960,1952,2144,2048
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
def residual(array):
 d=array[seam,x0:x1]-array[seam-1,x0:x1]
 g=(array[seam-1,x0:x1]-array[seam-2,x0:x1]+array[seam+1,x0:x1]-array[seam,x0:x1])/2
 return d-g,d,g
rr,cross,grad=residual(a);color=(a[seam,x0:x1]+a[seam-1,x0:x1])/2
wall=lambda rgb:smooth((rgb[...,0]-rgb[...,1]+8)/16)*smooth((rgb[...,1]-rgb[...,2]+8)/16)*smooth((rgb[...,0]-120)/35)
valid=(np.max(abs(grad),axis=1)<15)&(np.max(abs(cross),axis=1)<40)&(wall(color)>.9)
profile=np.zeros_like(rr);confidence=np.zeros(x1-x0,np.float32)
for j in range(x1-x0):
 lo=max(0,j-16);hi=min(x1-x0,j+17);ix=np.arange(lo,hi)
 use=valid[ix]&(np.linalg.norm(color[ix]-color[j],axis=1)<32)
 if not valid[j] or use.sum()<3:continue
 ix=ix[use];median=np.median(rr[ix],axis=0)
 weights=np.exp(-((ix-j)/7.)**2/2)*np.maximum(0,1-np.max(abs(rr[ix]-median),axis=1)/16)
 if weights.sum()<.2:continue
 profile[j]=np.clip((rr[ix]*weights[:,None]).sum(axis=0)/weights.sum(),-24,24)
 confidence[j]=1
good=np.flatnonzero(confidence>0)
assert len(good)>100
profile=np.stack([np.interp(np.arange(x1-x0),good,profile[good,c]) for c in range(3)],axis=1).astype(np.float32)
kernel=np.exp(-(np.arange(-8,9)/4.)**2/2);kernel/=kernel.sum()
profile=np.stack([np.convolve(np.pad(profile[:,c],(8,8),mode='edge'),kernel,mode='valid') for c in range(3)],axis=1).astype(np.float32)
ys=np.arange(y0,y1);normal=1-smooth(abs(ys-(seam-.5))/95.5)
tang=smooth(np.minimum(np.arange(x1-x0)+.5,x1-x0-np.arange(x1-x0)-.5)/24)
roi=a[y0:y1,x0:x1]
# Follow the existing wall-plane slope in the correction field only. No image
# pixels move: x_anchor=x+(y-2047.5) continues the observed diagonal at dx/dy~-1.
anchors=np.arange(x1-x0)[None,:]+(ys-(seam-.5))[:,None]
transported=np.stack([np.interp(anchors,np.arange(x1-x0),profile[:,c]) for c in range(3)],axis=2)
upper=np.stack([np.interp(anchors,np.arange(x1-x0),a[seam-1,x0:x1,c]) for c in range(3)],axis=2)
lower=np.stack([np.interp(anchors,np.arange(x1-x0),a[seam,x0:x1,c]) for c in range(3)],axis=2)
refcolors=np.where((ys<seam)[:,None,None],upper,lower)
material=np.exp(-np.mean((roi-refcolors)**2,axis=2)/(2*32**2))*wall(roi)
material[material<.03]=0
field=transported*np.where(ys<seam,.5,-.5)[:,None,None]*.98*normal[:,None,None]*tang[None,:,None]*material[:,:,None]
field=np.clip(field,-12,12)
prior=previous[y0:y1,x0:x1]
field=np.minimum(np.maximum(field,-12-prior),12-prior).astype(np.float32)
out=src.copy();out[y0:y1,x0:x1]=np.rint(np.clip(roi+field,0,255)).astype('uint8')
actual=out.astype(np.int16)-src.astype(np.int16);cumulative=out.astype(np.int16)-geo.astype(np.int16);changed=np.any(actual!=0,axis=2)
assert np.abs(actual).max()<=12 and np.abs(cumulative).max()<=12
assert not changed[:y0].any() and not changed[y1:].any() and not changed[:,:x0].any() and not changed[:,x1:].any()
Image.fromarray(out).save(O/'core4096.png')
np.savez_compressed(O/'wall-field.npz',field=field,coreBox=np.array([x0,y0,x1,y1]),estimatedSeamResidual=profile,validEstimateMask=valid,previousCarriedToneRGB=prior,cumulativeFloatRGB=prior+field)
mask=np.max(abs(field),axis=2)/12
Image.fromarray(np.rint(mask*255).astype('uint8')).save(O/'wall-mask.png')
fullmask=np.zeros((4096,4096),np.uint8);fullmask[y0:y1,x0:x1]=np.rint(mask*255).astype('uint8');Image.fromarray(fullmask).save(O/'support-mask.png')
outf=out.astype(np.float32);after,_,_=residual(outf)
metric_mask=valid&(np.arange(x1-x0)>=24)&(np.arange(x1-x0)<x1-x0-24)
metrics={'beforeMeanAbsoluteResidualRGB':float(abs(rr[metric_mask]).mean()),'afterMeanAbsoluteResidualRGB':float(abs(after[metric_mask]).mean()),'sampleColumns':int(metric_mask.sum()),'interpretation':'Same source-selected low-gradient wall columns, averaged absolute per-channel local first-derivative excess; not a texture-unification or acceptance score.'}
metrics['reductionPercent']=100*(1-metrics['afterMeanAbsoluteResidualRGB']/metrics['beforeMeanAbsoluteResidualRGB'])
boards=[]
for name,box in [('wall-full-support',[2488,1920,2992,2176]),('root-focus',[2720,1970,2900,2130])]:
 before=Image.fromarray(src).crop(box);result=Image.fromarray(out).crop(box)
 board=Image.new('RGB',(before.width,before.height*2+40),(32,32,32));draw=ImageDraw.Draw(board);draw.text((2,3),'BEFORE combined geometry',fill='white');board.paste(before,(0,20));draw.text((2,before.height+23),'AFTER RGB only',fill='white');board.paste(result,(0,before.height+40))
 p=Q/(name+'-before-after.png');board.save(p);boards.append({**rec(p),'coreBoxXYXYHalfOpen':box,'pixels':list(board.size),'layout':'before top with20px label; after bottom with20px label','resampling':'none','actuallyViewed':False})
yy,xx=np.where(changed)
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'Finish the previously missed left portion of the same continuous wall plane across y2048, after geometry-v2 composition.','input':rec(ip),'colorBudgetBaseline':{**rec(gp),'role':'The exact same saved geometry applied to the original candidate, excluding all tone adjustments'},'priorTone':rec(T/'tone-v1/core4096.png'),'savedGeometryField':rec(T/'geometry-v2/flow-correction.npz'),'operation':'Bounded additive RGB field only. Existing geometry is retained; no second warp, spatial filtering, image blur, or resampling. Only correction estimates are smoothed.','supportCoreXYXYHalfOpen':[x0,y0,x1,y1],'scopeDecision':'Original-pixel expanded view confirms the same missed wall plane extends left to aboutx2550; green foliage and dark/high-gradient contours are excluded by color/gradient confidence.','parameters':{'seamY':2048,'normalHalfWidth':96,'tangentTaper':24,'gain':.98,'profileRadius':16,'profileSpatialSigma':7,'compatibleColorEuclideanMax':32,'materialSimilaritySigma':32,'profileHoleFill':'linear interpolation of compatible valid estimates, followed by sigma4 field smoothing','fieldPlaneTransport':'x_anchor=x+(y-2047.5); correction estimates only, no image pixel movement','singlePassCapPerChannel':12,'cumulativeCapPerChannel':12,'cumulativeFormula':'priorToneRGB=combinedInput-geometryOnlyBaseline; newField=clip(requested,-12-priorToneRGB,12-priorToneRGB)'},'fields':{'localFloatCorrection':rec(O/'wall-field.npz'),'localMask':rec(O/'wall-mask.png'),'wholeCoreSupportMask':rec(O/'support-mask.png')},'output':rec(O/'core4096.png'),'maxActualAdditionalChangeRGB':np.abs(actual).max(axis=(0,1)).tolist(),'maxActualCumulativeToneChangeRGB':np.abs(cumulative).max(axis=(0,1)).tolist(),'changedPixelCount':int(changed.sum()),'actualChangedBoundsCoreXYXYHalfOpen':[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],'checks':{'allPixelsOutsideLocalSupportIdentical':True,'cumulativeBudgetIncludesPriorCarriedTone':True,'noNewGeometricTransform':True,'sourceFilesUnchanged':sha(ip)=='d0b672162e0daf6b0c829cbc0f4a482f5c95c2a50cd718bf61fee2bade8e14a1'},'seamMetrics':metrics,'beforeAfterBoards':boards,'derivationScript':rec(Path(__file__)),'formalAccepted':False,'visualReviewPending':True}
(O/'processing.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':report['output'],'maxAdditionalRGB':report['maxActualAdditionalChangeRGB'],'maxCumulativeToneRGB':report['maxActualCumulativeToneChangeRGB'],'changedPixels':report['changedPixelCount'],'metrics':metrics}))

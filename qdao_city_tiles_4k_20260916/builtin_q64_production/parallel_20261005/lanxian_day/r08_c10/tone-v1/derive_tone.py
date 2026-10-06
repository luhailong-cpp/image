"""Bounded local additive RGB correction; source geometry and pixels never resampled."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent; T=O.parent; Q=O/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:{'file':str(p),'sha256':sha(p)}
cp=T/'candidate/core4096.png';ep=T/'candidate/extended4326.png'
assert sha(cp)=='1a2bb992de62dce69c9e77fb7ad0163aa7fa96f402156e8f8268ff8a09ccdd0f'
src=np.array(Image.open(cp).convert('RGB'));ext=np.array(Image.open(ep).convert('RGB'))
assert np.array_equal(ext[115:4211,115:4211],src)
a=src.astype(np.float32);total=np.zeros_like(a)
ops=[('V1','x',1024,1040,1300),('V2','x',2048,1036,1470),('V3','x',2048,1934,2240),('V4','x',2048,3008,3280)]
ops += [(f'H{r}c{c}','y',s,x0,x0+512) for r,s in [(1,1024),(2,2048)] for c,x0 in [(1,768),(2,1792),(3,2816)]]
excluded=[[0,0,512,4096],[220,1110,280,1175],[620,1110,685,1175],[3150,2970,3225,3060]]
H=32;gain=.85;profile_cap=20.;pass_cap=9.;cumulative_cap=12.;color_sigma=28.;taper=20
def smooth(z):
 z=np.clip(z,0,1);return z*z*(3-2*z)
def jump(array,axis,s,t0,t1):
 b=array if axis=='x' else array.transpose(1,0,2)
 cross=b[t0:t1,s]-b[t0:t1,s-1]
 grad=(b[t0:t1,s-1]-b[t0:t1,s-2]+b[t0:t1,s+1]-b[t0:t1,s])/2
 return cross-grad,cross,grad
records=[];fields={}
for name,axis,s,t0,t1 in ops:
 b=a if axis=='x' else a.transpose(1,0,2)
 r,cross,grad=jump(a,axis,s,t0,t1)
 color=(b[t0:t1,s]+b[t0:t1,s-1])/2
 valid=(np.max(np.abs(grad),axis=1)<15)&(np.max(np.abs(cross),axis=1)<40)
 profile=np.zeros_like(r)
 confidence=np.zeros(t1-t0,np.float32)
 for j in range(t1-t0):
  lo=max(0,j-12);hi=min(t1-t0,j+13);ix=np.arange(lo,hi)
  compatible=np.linalg.norm(color[ix]-color[j],axis=1)<42
  good=valid[ix]&compatible
  if not valid[j] or good.sum()<3:continue
  ix=ix[good]
  # Smooth a correction estimate only. Image pixels are never filtered.
  med=np.median(r[ix],axis=0)
  robust=np.maximum(0,1-np.max(np.abs(r[ix]-med),axis=1)/18)
  w=np.exp(-((ix-j)/5.)**2/2)*robust
  if w.sum()<.2:continue
  profile[j]=np.clip((r[ix]*w[:,None]).sum(axis=0)/w.sum(),-profile_cap,profile_cap)
  confidence[j]=1
 # Normal taper goes to zero with zero derivative at either outer band edge.
 n=np.arange(s-H,s+H)
 nd=np.minimum(np.abs(n-(s-.5))/(H-.5),1)
 normal=1-smooth(nd)
 tang=smooth(np.minimum(np.arange(t1-t0)+.5,t1-t0-np.arange(t1-t0)-.5)/taper)
 roi=b[t0:t1,s-H:s+H]
 sidecolors=np.where((n<s)[None,:,None],b[t0:t1,s-1,None,:],b[t0:t1,s,None,:])
 material=np.exp(-np.mean((roi-sidecolors)**2,axis=2)/(2*color_sigma**2))
 material[material<.05]=0
 field=np.clip(profile[:,None,:]*np.where(n<s,.5,-.5)[None,:,None]*gain*normal[None,:,None]*tang[:,None,None]*confidence[:,None,None]*material[:,:,None],-pass_cap,pass_cap)
 if axis=='x':
  box=[s-H,t0,s+H,t1];f=field
 else:
  box=[t0,s-H,t1,s+H];f=field.transpose(1,0,2)
 x0,y0,x1,y1=box
 for ex0,ey0,ex1,ey1 in excluded:
  xx0,yy0=max(x0,ex0),max(y0,ey0);xx1,yy1=min(x1,ex1),min(y1,ey1)
  if xx0<xx1 and yy0<yy1:f[yy0-y0:yy1-y0,xx0-x0:xx1-x0]=0
 total[y0:y1,x0:x1]+=f
 fields[name]=f.astype(np.float32)
 profilepath=O/f'{name}-field.npz';np.savez_compressed(profilepath,field=f.astype(np.float32),coreBox=np.array(box),profile=profile,validProfileMask=valid,confidence=confidence)
 mask=np.max(np.abs(f),axis=2)/cumulative_cap
 maskpath=O/f'{name}-mask.png';Image.fromarray(np.rint(mask*255).astype('uint8')).save(maskpath)
 records.append({'id':name,'axis':axis,'coordinate':s,'tangentIntervalHalfOpen':[t0,t1],'supportCoreXYXYHalfOpen':box,'validMetricRows':valid.tolist(),'field':rec(profilepath),'mask':rec(maskpath),'maxSinglePassFieldAbsRGB':np.abs(f).max(axis=(0,1)).tolist(),'sourceResidualAbsMean':float(np.abs(r[valid]).mean())})
total=np.clip(total,-cumulative_cap,cumulative_cap)
out=np.rint(np.clip(a+total,0,255)).astype('uint8')
delta=out.astype(np.int16)-src.astype(np.int16);changed=np.any(delta!=0,axis=2)
for x0,y0,x1,y1 in excluded:assert not changed[y0:y1,x0:x1].any()
assert np.abs(delta).max()<=12
np.savez_compressed(O/'cumulative-correction-field.npz',field=total,coordinateSpace=np.array('core4096'))
Image.fromarray(np.rint(np.max(np.abs(total),axis=2)/12*255).astype('uint8')).save(O/'cumulative-mask.png')
Image.fromarray(out).save(O/'core4096.png')
extout=ext.copy();extout[115:4211,115:4211]=out
Image.fromarray(extout).save(O/'extended4326.png')
boards=[];outf=out.astype(np.float32)
for op in records:
 t0,t1=op['tangentIntervalHalfOpen'];axis=op['axis'];s=op['coordinate'];valid=np.array(op.pop('validMetricRows'))
 rr,dd,gg=jump(outf,axis,s,t0,t1)
 op['resultResidualAbsMean']=float(np.abs(rr[valid]).mean())
 op['residualAbsMeanReductionPercent']=100*(1-op['resultResidualAbsMean']/op['sourceResidualAbsMean'])
 op['metricScope']='Same source-selected low-gradient non-extreme seam samples only; not a score of all pixels or visual acceptance.'
 x0,y0,x1,y1=op['supportCoreXYXYHalfOpen'];box=[max(0,x0-24),max(0,y0-24),min(4096,x1+24),min(4096,y1+24)]
 before=Image.fromarray(src).crop(box);after=Image.fromarray(out).crop(box)
 board=Image.new('RGB',(before.width,before.height*2+40),(32,32,32));draw=ImageDraw.Draw(board)
 draw.text((2,3),op['id']+' BEFORE',fill='white');board.paste(before,(0,20))
 draw.text((2,before.height+23),op['id']+' AFTER',fill='white');board.paste(after,(0,before.height+40))
 p=Q/(op['id']+'-before-after.png');board.save(p)
 boards.append({'id':op['id'],**rec(p),'pixels':list(board.size),'coreBoxXYXYHalfOpen':box,'layout':'original-pixel before at [0,20], after at [0,height+40]','operation':'integer crop/paste only','resampling':'none','actuallyViewed':False})
npix=int(changed.sum());yy,xx=np.where(changed)
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'purpose':'Reduce confirmed local color discontinuities while retaining all source geometry and texture pixels.','inputs':{'core':rec(cp),'extended':rec(ep),'review':rec(T/'qa/vertical-and-guide-review.json')},'operation':'One additive field computed exclusively from the original candidate. Correction profiles are robustly smoothed, gated by local color similarity and low native gradients, with cubic spatial tapers. Output=round(clip(source+clip(sum(fields),-12,12))). Original image is never blurred, resampled, warped, or filtered.','parameters':{'normalHalfWidth':H,'tangentTaperPixels':taper,'profileNeighborhoodRadius':12,'profileSpatialSigma':5,'compatibleSeamColorEuclideanMax':42,'materialSimilaritySigma':color_sigma,'maxSideGradientChannel':15,'maxCrossJumpChannelForEstimate':40,'gain':gain,'profilePerChannelCap':profile_cap,'singlePassPerChannelCap':pass_cap,'cumulativePerChannelCap':cumulative_cap},'exclusionsCoreXYXYHalfOpen':excluded,'excludedAreasPixelIdentical':True,'deferredTextureOnlyFindings':['H3 brush-scale/material transition is not corrected by RGB; V1/V4 brush-scale mismatch also remains even where local mean color is adjusted.'],'passes':records,'cumulativeField':rec(O/'cumulative-correction-field.npz'),'cumulativeMask':rec(O/'cumulative-mask.png'),'outputs':{'core':rec(O/'core4096.png'),'extended':rec(O/'extended4326.png')},'maxCumulativeFloatFieldAbsRGB':np.abs(total).max(axis=(0,1)).tolist(),'maxActualChangeFromCandidateRGB':np.abs(delta).max(axis=(0,1)).tolist(),'changedPixelCount':npix,'changedBoundsCoreXYXYHalfOpen':[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],'checks':{'outsideAllLocalSupportsUnchanged':True,'coreLeft512Identical':True,'allTinyGeometryExclusionsUnchanged':True,'noSpatialResampling':True,'sourceHaloUnchanged':bool(np.array_equal(extout[:115],ext[:115]) and np.array_equal(extout[4211:],ext[4211:]) and np.array_equal(extout[:,:115],ext[:,:115]) and np.array_equal(extout[:,4211:],ext[:,4211:]))},'derivationScript':rec(Path(__file__)),'formalAccepted':False,'visualReviewPending':True}
(O/'processing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(Q/'comparison-derivation.json').write_text(json.dumps({'sources':report['inputs'],'outputs':report['outputs'],'boards':boards},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'outputs':report['outputs'],'maxActualChangeRGB':report['maxActualChangeFromCandidateRGB'],'changedPixels':npix,'metrics':[{'id':r['id'],'before':r['sourceResidualAbsMean'],'after':r['resultResidualAbsMean'],'reductionPercent':r['residualAbsMeanReductionPercent']} for r in records]}))


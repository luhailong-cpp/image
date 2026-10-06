from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/r09_c13';QA=ROOT/'qa/west-final/color-trial'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def weighted_median(values,weights):
    order=np.argsort(values);cs=np.cumsum(weights[order]);return values[order[np.searchsorted(cs,cs[-1]/2)]]

def main():
    QA.mkdir(parents=True,exist_ok=True)
    m=read(OUT/'manifest.json');src=OUT/'r09_c13.png';oldfile=Path(m['westSource'])
    assert sha(src)=='efbbbb109885acf3f5c87467cad3b4b2e5dc84939681647aea5dfb235752f4b5'
    assert sha(oldfile)==m['westSourceSha256']
    old=np.array(Image.open(oldfile).convert('RGB')).astype(np.float32)
    new=np.array(Image.open(src).convert('RGB')).astype(np.float32)
    # Adjacent, corresponding material estimates, extrapolated through at most2.5px.
    l=old[:,-4:];n=new[:,:4]
    ls=np.median(np.diff(l,axis=1),axis=1);ns=np.median(np.diff(n,axis=1),axis=1)
    lp=np.median(l[:,-2:],axis=1)+1.5*ls
    npred=np.median(n[:,:2],axis=1)-.5*ns
    raw=lp-npred
    guide=(lp+npred)/2
    edge=np.maximum(np.max(np.abs(np.diff(l,axis=1)),axis=(1,2)),np.max(np.abs(np.diff(n,axis=1)),axis=(1,2)))
    edge_y=np.max(np.abs(np.gradient(guide,axis=0)),axis=1)
    reliable=(edge<10)&(edge_y<9)&(np.max(np.abs(raw),axis=1)<40)
    # Robust33-row window, guided by neighboring same-material RGB. Large contour gradients
    # are rejected, not treated as brightness errors. Median is followed by a guided5-row
    # average of the correction only; native artwork is never filtered or resampled.
    med=np.zeros((4096,3),np.float32);counts=np.zeros(4096,np.int32)
    for y in range(4096):
        ids=np.arange(max(0,y-16),min(4096,y+17));sd=np.linalg.norm(guide[ids]-guide[y],axis=1)
        w=np.exp(-.5*((ids-y)/8)**2)*np.exp(-.5*(sd/20)**2)*reliable[ids]
        counts[y]=int(np.sum(w>.03))
        if w.sum()<.1:
            ids=np.arange(max(0,y-48),min(4096,y+49));sd=np.linalg.norm(guide[ids]-guide[y],axis=1)
            w=np.exp(-.5*((ids-y)/24)**2)*np.exp(-.5*(sd/24)**2)*reliable[ids]
        if w.sum()<.01:
            med[y]=0
        else:
            med[y]=[weighted_median(raw[ids,c],w) for c in range(3)]
    rows=med.copy()
    for y in range(4096):
        ids=np.arange(max(0,y-2),min(4096,y+3));sd=np.linalg.norm(guide[ids]-guide[y],axis=1)
        w=np.exp(-.5*((ids-y)/1.2)**2)*np.exp(-.5*(sd/16)**2)
        rows[y]=np.sum(med[ids]*w[:,None],axis=0)/w.sum()
    rows=np.clip(rows,-32,32)
    yy=np.arange(4096);xx=np.arange(256)
    north=np.maximum(1-smooth((yy-32)/18),smooth((yy-300)/16)*(1-smooth((yy-344)/24)))
    wy=np.maximum(north,smooth((yy-1004)/96)*(1-smooth((yy-1600)/96)))
    wx=1-smooth(xx/256)
    field=rows[:,None,:]*wy[:,None,None]*wx[None,:,None]
    mask=wy[:,None]*wx[None,:]
    corrected=np.clip(np.rint(new[:,:256]+field),0,255).astype(np.uint8)
    Image.fromarray(corrected).save(QA/'native-band.png')
    Image.fromarray(np.uint8(np.rint(mask*255))).save(QA/'mask.png')
    np.save(QA/'color-field.npy',field);np.save(QA/'row-color-estimates.npy',rows)
    result=new.astype(np.uint8).copy();result[:,:256]=corrected
    assert np.array_equal(result[:,256:],new[:,256:])
    assert np.array_equal(result[448:1004],new[448:1004]) and np.array_equal(result[1696:],new[1696:])
    pair=np.concatenate([old[:,-160:].astype(np.uint8),result[:,:512]],axis=1)
    qa=[]
    def save(name,box):
        p=QA/name;Image.fromarray(pair).crop(box).save(p)
        q=dict(**ref(p),pixels=[box[2]-box[0],box[3]-box[1]],pairCropLTRB=box,sharedEdgeImageX=160-box[0],return256ImageX=416-box[0],actuallyViewed=False,scale=1)
        qa.append(q);write(str(p)+'.generation.json',dict(**q,derivedFrom=[ref(src),ref(oldfile),ref(QA/'native-band.png')],operation='native_pixel_QA_crop_no_resizing'))
    save('north-all.png',[0,0,672,608])
    save('paving-all.png',[0,844,672,1856])
    for name,y in [('internal1024',1024),('repair1100',1100),('fade1600',1600)]: save(name+'.png',[0,y-128,672,y+128])
    metrics=[]
    for y0,y1 in [(0,320),(1100,1600)]:
        before=new[y0:y1,0]-old[y0:y1,-1];after=result[y0:y1,0].astype(float)-old[y0:y1,-1]
        metrics.append(dict(yRange=[y0,y1],medianRGBJumpBefore=np.median(before,axis=0).tolist(),medianRGBJumpAfter=np.median(after,axis=0).tolist(),meanAbsoluteJumpBefore=float(abs(before).mean()),meanAbsoluteJumpAfter=float(abs(after).mean())))
    rec=dict(createdAt=datetime.now(timezone.utc).isoformat(),kind='native_pixel_color_only_trial',input=ref(src),oldWesternSupport=ref(oldfile),
        algorithm='Per-row old last4 and new first4 native support. Robust2px medians with median local slope extrapolate to boundary. Reject support x-gradients>=10 or row-guide gradients>=9 or raw correction magnitude>=40. Guided33-row weighted median (97-row fallback only if sparse), then guided5-row smoothing of correction field only. RGB correction clamped32; smoothstep return to zero at x256. No spatial coordinate change.',
        coreYRanges=[[0,32],[316,344],[1100,1600]],transitionYRanges=[[32,50],[300,316],[344,368],[1004,1100],[1600,1696]],editableXRange=[0,256],
        protectedNorthYRange=[50,300],protectionReason='The old-left support is a narrow post-shadow contour here; its native last-column gradient and horizontal rail crossing must not be treated as a color offset. There is no sufficiently broad same-plane support to justify a flat correction.',
        transitionReason='Zero-ended color-field ramps prevent horizontal bands. North scope was narrowed after rejecting the first trial, to avoid falsely correcting a natural post/rail contour.',
        maximumAllowedColorCorrectionRGB=32,actualMaximumColorCorrectionRGB=np.max(abs(field),axis=(0,1)).tolist(),geometryDisplacement=0,artworkBlurred=False,artworkResampled=False,sourceScale=1,
        oldWesternTileUnchanged=True,productionOutputModified=False,metrics=metrics,fields=[ref(QA/v) for v in ['native-band.png','mask.png','color-field.npy','row-color-estimates.npy']],qa=qa,visualReviewPending=True,formalAccepted=False,clientVerified=False,navigationVerified=False)
    write(QA/'trial-record.json',rec);print(json.dumps(dict(metrics=metrics,actualMax=rec['actualMaximumColorCorrectionRGB'],qaCount=len(qa))))

if __name__=='__main__':main()

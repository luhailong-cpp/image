"""Bounded local registration of existing groove contours; no synthesis or color edit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
import numpy as np
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
TILE = OUT.parent
SOURCE = TILE / 'candidate/core4096.png'
EXPECTED = '1a2bb992de62dce69c9e77fb7ad0163aa7fa96f402156e8f8268ff8a09ccdd0f'
VENDOR = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
sys.path.insert(0, str(VENDOR))
import cv2

CASES = [
    dict(id='HG01a',axis='y',center=1139,box=[200,1090,290,1210],thresholds=[100,180],reviewBox=[180,1040,310,1260]),
    dict(id='HG01b',axis='y',center=1139,box=[600,1090,710,1210],thresholds=[100,180],reviewBox=[570,1040,740,1260]),
    dict(id='HG02',axis='x',center=3187,box=[3120,2960,3260,3080],thresholds=[210,170],reviewBox=[3070,2910,3310,3130]),
]

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save_image(name, array):
    p=OUT/name
    im=array if isinstance(array, Image.Image) else Image.fromarray(array)
    im.save(p)
    return dict(file=str(p),sha256=sha(p),pixels=list(im.size))

def anchors(gray, case):
    x0,y0,x1,y1=case['box']; profile=gray[y0:y1,x0:x1]
    if case['axis']=='x': profile=profile.T; t0=x0; origin=y0
    else: t0=y0; origin=x0
    ts=np.arange(t0,t0+len(profile),dtype=np.float64)
    a,b=case['thresholds']; edge=[]
    for row in profile:
        down=np.where((row[:-1]>=a)&(row[1:]<a))[0]
        up=np.where((row[:-1]<b)&(row[1:]>=b))[0]
        mn=int(np.argmin(row)); down=down[down<mn];up=up[up>=mn]
        if not len(down) or not len(up): edge.append([np.nan,np.nan]);continue
        k=down[0] if case['id']=='HG02' else down[-1]; l=up[0]
        edge.append([origin+k+(a-row[k])/(row[k+1]-row[k]),origin+l+(b-row[l])/(row[l+1]-row[l])])
    edge=np.asarray(edge)
    for k in range(2):
        ok=np.isfinite(edge[:,k]);edge[:,k]=np.interp(ts,ts[ok],edge[ok,k])
    return ts,edge

def cosine_window(t,start,flat_start,flat_end,end):
    result=np.ones_like(t,dtype=np.float64)
    left=t<flat_start;right=t>flat_end
    result[left]=.5-.5*np.cos(np.pi*np.clip((t[left]-start)/(flat_start-start),0,1))
    result[right]=.5+.5*np.cos(np.pi*np.clip((t[right]-flat_end)/(end-flat_end),0,1))
    return result

def main():
    assert sha(SOURCE)==EXPECTED
    source=np.array(Image.open(SOURCE).convert('RGB'));assert source.shape==(4096,4096,3)
    gray=source.mean(2);result=source.copy()
    flow_x=np.zeros((4096,4096),np.float32);flow_y=flow_x.copy();weight=flow_x.copy()
    measurements=[];fields={}
    for c in CASES:
        x0,y0,x1,y1=c['box'];ts,edge=anchors(gray,c);dt=ts-c['center']
        stable=(np.abs(dt)>=9)&(np.abs(dt)<=35)
        fits=np.array([np.polyfit(dt[stable],edge[stable,k],1) for k in range(2)])
        target=np.array([np.polyval(f,dt) for f in fits]).T
        raw=edge-target
        # Smooth the displacement estimate only, never the RGB image.
        disp=cv2.GaussianBlur(raw.astype(np.float32),(1,3),sigmaX=0,sigmaY=.45)
        tw=cosine_window(ts,ts[0],c['center']-18,c['center']+18,ts[-1])
        ns=np.arange(x0,x1,dtype=np.float64) if c['axis']=='y' else np.arange(y0,y1,dtype=np.float64)
        n=ns[None,:];left=target[:,0,None];right=target[:,1,None]
        u=np.clip((n-left)/(right-left),0,1)
        local=disp[:,0,None]*(1-u)+disp[:,1,None]*u
        cross=np.ones_like(local)
        outside_left=n<left-5;outside_right=n>right+5
        cross=np.where(outside_left,.5-.5*np.cos(np.pi*np.clip((n-(left-16))/11,0,1)),cross)
        cross=np.where(outside_right,.5+.5*np.cos(np.pi*np.clip((n-(right+5))/11,0,1)),cross)
        border=cosine_window(ns,ns[0],ns[0]+7,ns[-1]-7,ns[-1])
        weights=cross*tw[:,None]*border[None,:]
        applied=(local*weights).astype(np.float32)
        if c['axis']=='x':applied=applied.T;weights=weights.T
        assert np.max(np.abs(applied))<=4.0
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
        dx=applied if c['axis']=='y' else np.zeros_like(applied)
        dy=applied if c['axis']=='x' else np.zeros_like(applied)
        # One subpixel bilinear reconstruction, no blur, sharpening, alpha blend, or tone change.
        warped=cv2.remap(source,xx+dx,yy+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
        active=(np.abs(applied)>1e-7)
        patch=result[y0:y1,x0:x1];patch[active]=warped[active]
        flow_x[y0:y1,x0:x1]=dx;flow_y[y0:y1,x0:x1]=dy;weight[y0:y1,x0:x1]=weights
        fields[c['id']+'_t']=ts;fields[c['id']+'_source_edges']=edge
        fields[c['id']+'_target_edges']=target;fields[c['id']+'_raw_displacement']=raw
        fields[c['id']+'_smoothed_displacement']=disp
        # Positive determinant verifies that the small local warp does not fold the contour.
        derivative=np.gradient(dx,axis=1) if c['axis']=='y' else np.gradient(dy,axis=0)
        measurement=dict(c,fitSlopesIntercepts=fits.tolist(),maxAbsFlowPixels=float(np.abs(applied).max()),
            minMappingJacobian=float((1+derivative).min()),supportMethod='cosine taper along and across groove; zero at support rectangle boundary',
            contourAnchors='falling/rising intensity threshold crossings of existing bevel and dark groove; target straight local continuation fit only from stable bands 9..35 pixels away')
        measurements.append(measurement)
    active=(np.abs(flow_x)+np.abs(flow_y))>1e-7
    changed=np.any(source!=result,axis=2)
    assert not np.any(changed&~active)
    assert np.array_equal(result[~active],source[~active])
    output=save_image('core4096.png',result)
    masks=[save_image('support-mask.png',(active*255).astype(np.uint8)),save_image('taper-weight.png',np.rint(weight*255).astype(np.uint8)),save_image('changed-pixels.png',(changed*255).astype(np.uint8))]
    fields.update(flow_x=flow_x,flow_y=flow_y,taper_weight=weight)
    npz=OUT/'flow-correction.npz';np.savez_compressed(npz,**fields)
    evidence=[];board=Image.new('RGB',(512,756),(28,28,28));draw=ImageDraw.Draw(board)
    for i,c in enumerate(CASES):
        b=c['reviewBox'];before=Image.fromarray(source).crop(b);after=Image.fromarray(result).crop(b)
        e1=save_image(c['id']+'-before.png',before);e2=save_image(c['id']+'-after.png',after)
        y=i*252;draw.text((4,y+6),c['id']+' BEFORE '+str(b),fill='white');draw.text((260,y+6),c['id']+' AFTER',fill='white')
        board.paste(before,(0,y+32));board.paste(after,(256,y+32))
        evidence.append(dict(id=c['id'],coreBox=b,before=e1,after=e2,boardBoxes=[[0,y+32,b[2]-b[0],y+252],[256,y+32,256+b[2]-b[0],y+252]]))
        _,after_edges=anchors(result.mean(2),c)
        m=next(m for m in measurements if m['id']==c['id']);t=fields[c['id']+'_t'];inner=np.abs(t-c['center'])<=6
        target=fields[c['id']+'_target_edges'];before_edges=fields[c['id']+'_source_edges']
        m['diagnosticOnlyContourResidualsNearBoundary']={'scope':'center +/-6 pixels; threshold landmarks, not visual acceptance','beforeMaxAbsPixels':np.max(np.abs(before_edges[inner]-target[inner]),axis=0).tolist(),'afterMaxAbsPixels':np.max(np.abs(after_edges[inner]-target[inner]),axis=0).tolist()}
    board_info=save_image('before-after-native-board.png',board)
    assert sha(SOURCE)==EXPECTED
    report=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),source=dict(file=str(SOURCE),sha256=EXPECTED,pixels=[4096,4096]),output=output,
        operation='local existing-contour displacement registration only',maxAllowedFlowPixels=4,
        flowConvention='output(x,y) samples source(x+flow_x,y+flow_y); positive displacement is a source sampling offset',
        resampling=dict(performed=True,method='OpenCV INTER_LINEAR, one pass only in nonzero local flow support',subpixel=True,imageBlurApplied=False,sharpeningApplied=False,colorCorrectionApplied=False,alphaFeatherApplied=False),
        displacementEstimateSmoothing=dict(appliesTo='displacement estimates only, not RGB',kernel=[1,3],sigmaAlongContour=.45),
        support=measurements,masks=masks,flow=dict(file=str(npz),sha256=sha(npz),arrays=list(fields)),
        unchangedOutsideSupportVerified=True,sourceUnchangedVerified=True,changedPixels=int(changed.sum()),activeFlowPixels=int(active.sum()),
        boards=[board_info],qaCrops=evidence,visualInspectionPerformed=False,formalAccepted=False,
        pending='Actual original-scale full-contour and support-boundary review required before recording residuals.')
    (OUT/'registration.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':output,'maxFlow':[m['maxAbsFlowPixels'] for m in measurements],'minJacobians':[m['minMappingJacobian'] for m in measurements],'changedPixels':int(changed.sum()),'report':str(OUT/'registration.json')}))

if __name__=='__main__':main()

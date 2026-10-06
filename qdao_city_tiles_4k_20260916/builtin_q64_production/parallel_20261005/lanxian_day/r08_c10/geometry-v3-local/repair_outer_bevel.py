"""Register only the remaining outer gray bevel edge on the fully corrected tone-v2 input."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw

OUT=Path(__file__).resolve().parent
TILE=OUT.parent
SOURCE=TILE/'tone-v2-local/core4096.png'
EXPECTED='129b7fc447218e4bcc29359dedf87eee1c8124f10bbaa5487a61756b0f30a200'
BOX=[2760,1992,2910,2104]
CENTER=2048
LEVELS=[180,190,205]
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,arr):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    im=arr if isinstance(arr,Image.Image) else Image.fromarray(arr);im.save(p)
    return {'file':str(p),'sha256':sha(p),'pixels':list(im.size)}

def cosine(t,start,a,b,end):
    w=np.ones_like(t,dtype=float)
    left=t<a;right=t>b
    w[left]=.5-.5*np.cos(np.pi*np.clip((t[left]-start)/(a-start),0,1))
    w[right]=.5+.5*np.cos(np.pi*np.clip((t[right]-b)/(end-b),0,1))
    return w

def track(gray):
    ts=np.arange(BOX[1],BOX[3]);tracks=[];dark=[]
    for y in ts:
        expected=2830-.92*(y-CENTER);x0=int(expected)-16;v=gray[y,x0:x0+34];row=[]
        for level,offset in zip(LEVELS,[-1,0,1.5]):
            ks=np.where((v[:-1]<level)&(v[1:]>=level))[0]
            if not len(ks):raise ValueError(f'No existing outer-edge crossing at y={y}, level={level}')
            ps=np.array([x0+k+(level-v[k])/(v[k+1]-v[k]) for k in ks])
            row.append(float(ps[np.argmin(abs(ps-(expected+offset)))]))
        tracks.append(row)
        center_guess=2803-.84*(y-CENTER);d0=int(center_guess)-11
        dark.append(d0+int(np.argmin(gray[y,d0:d0+24])))
    return ts,np.array(tracks),np.array(dark)

def main():
    assert sha(SOURCE)==EXPECTED
    before=np.array(Image.open(SOURCE).convert('RGB'));assert before.shape==(4096,4096,3)
    gray=before.mean(2);ts,edges,dark=track(gray);dt=ts-CENTER
    stable=(abs(dt)>=10)&(abs(dt)<=34)
    fits=np.array([np.polyfit(dt[stable],edges[stable,k],1) for k in range(3)])
    target=np.array([np.polyval(f,dt) for f in fits]).T
    raw=edges-target
    displacement=cv2.GaussianBlur(raw.astype(np.float32),(1,3),sigmaX=0,sigmaY=.4)
    x0,y0,x1,y1=BOX;xs=np.arange(x0,x1,dtype=float)
    local=np.array([np.interp(xs,target[i],displacement[i]) for i in range(len(ts))])
    cross=np.ones_like(local)
    for i in range(len(ts)):
        # Preserve the full visible edge transition while tapering through flat existing material.
        cross[i]=cosine(xs,target[i,0]-15,target[i,0]-4,target[i,2]+4,target[i,2]+15)
        protect=np.clip((xs-(dark[i]+9))/6,0,1)
        protect=.5-.5*np.cos(np.pi*protect)
        cross[i]*=protect
    along=cosine(ts,ts[0],CENTER-18,CENTER+18,ts[-1])
    border=cosine(xs,xs[0],xs[0]+6,xs[-1]-6,xs[-1])
    weight=cross*along[:,None]*border[None,:]
    dx=(local*weight).astype(np.float32);dy=np.zeros_like(dx)
    protected=np.broadcast_to(xs[None,:],dx.shape)<=dark[:,None]+9
    assert np.all(dx[protected]==0)
    assert abs(dx).max()<=4
    yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
    warped=cv2.remap(before,xx+dx,yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
    after=before.copy();active=abs(dx)>1e-7
    after[y0:y1,x0:x1][active]=warped[active]
    assert np.array_equal(after[y0:y1,x0:x1][protected],before[y0:y1,x0:x1][protected])
    full_dx=np.zeros((4096,4096),np.float32);full_dx[y0:y1,x0:x1]=dx
    full_dy=np.zeros_like(full_dx);full_weight=np.zeros_like(full_dx);full_weight[y0:y1,x0:x1]=weight
    full_active=abs(full_dx)>1e-7;changed=np.any(before!=after,axis=2)
    assert not np.any(changed&~full_active)
    output=save('core4096.png',after)
    masks=[save('support-mask.png',(full_active*255).astype(np.uint8)),save('taper-weight.png',np.rint(full_weight*255).astype(np.uint8)),save('changed-pixels.png',(changed*255).astype(np.uint8))]
    fp=OUT/'outer-bevel-flow.npz'
    np.savez_compressed(fp,flow_x=full_dx,flow_y=full_dy,local_dx=dx,local_dy=dy,local_support_weight=weight.astype(np.float32),support_box=np.array(BOX,np.int32),taper_weight=full_weight,source_outer_contours=edges,target_outer_contours=target,source_dark_centers=dark,protected_local_mask=protected,raw_displacement=raw,smoothed_displacement=displacement,fit_slopes_intercepts=fits,core_y=ts,threshold_levels=np.array(LEVELS))
    _,after_edges,after_dark=track(after.mean(2));inner=abs(dt)<=6
    comparisons=[]
    for name,box in [('root-focus',[2720,1970,2900,2130]),('wall-full-support',[2488,1920,2992,2176]),('outer-bevel-detail',[2784,2016,2860,2080])]:
        first=Image.fromarray(before).crop(box);second=Image.fromarray(after).crop(box)
        board=Image.new('RGB',(first.width,first.height*2+40),(28,28,28));draw=ImageDraw.Draw(board)
        draw.text((3,4),'BEFORE current tone-v2',fill='white');board.paste(first,(0,20))
        draw.text((3,first.height+24),'AFTER outer bevel only',fill='white');board.paste(second,(0,first.height+40))
        info=save('qa/'+name+'-before-after.png',board);info.update(coreBoxLTRB=box,resampling='none; integer crop and paste',layout='before upper; after lower; separate20px labels');comparisons.append(info)
    ys,xp=np.where(full_active)
    report={'schemaVersion':1,'createdAt':datetime.now(timezone.utc).isoformat(),'source':{'file':str(SOURCE),'sha256':EXPECTED,'role':'Current tone-v2-local includes all previous geometry and RGB corrections'},'output':output,'operation':'One NEW local displacement field on the gray bevel OUTER transition only; no previous field is reapplied','supportRectangleLTRB':BOX,'actualFlowBoundsLTRB':[int(xp.min()),int(ys.min()),int(xp.max()+1),int(ys.max()+1)],'actualFlowPixels':int(full_active.sum()),'changedPixels':int(changed.sum()),'maxAllowedFlowPixels':4,'maxAppliedDxPixels':float(abs(dx).max()),'appliedDyPixels':0,'minMappingJacobian':float((1+np.gradient(dx,axis=1)).min()),'fitSlopesIntercepts':fits.tolist(),'referenceContours':'Three levels across existing gray-bevel-to-beige-wall transition, not darkest-row alone','levels':LEVELS,'fitRows':'10..34px above/below y2048; central discontinuity excluded','darkGrooveProtection':'All local output pixels x <= measured existing dark center +9 have exactly zero added flow and are byte-identical to current input','allDarkCentersUnchanged':bool(np.array_equal(dark,after_dark)),'protectedPixelsByteIdentical':True,'outsideSupportUnchanged':True,'priorFlowReapplied':False,'resampling':{'additionalPasses':1,'method':'cv2.INTER_LINEAR only within new local nonzero field','subpixel':True,'RGBBlur':False,'RGBColorChange':False,'sharpening':False,'fieldSmoothingOnly':{'kernel':[1,3],'sigmaY':.4}},'masks':masks,'flow':{'file':str(fp),'sha256':sha(fp),'convention':'Output(x,y) samples CURRENT input(x+dx,y), not the old raw candidate'},'diagnostics':{'centralBeforeMaxAbsoluteContourResidual':np.max(abs((edges-target)[inner]),axis=0).tolist(),'centralAfterMaxAbsoluteContourResidual':np.max(abs((after_edges-target)[inner]),axis=0).tolist(),'threshold190SourceY2047':float(edges[np.where(ts==2047)[0][0],1]),'threshold190SourceY2048':float(edges[np.where(ts==2048)[0][0],1]),'interpretation':'Contour diagnostic supports, but does not replace, actual native full-plane review'},'qaBoards':comparisons,'visualInspectionPerformed':False,'formalAccepted':False,'sourceUnchangedVerified':sha(SOURCE)==EXPECTED,'script':{'file':str(Path(__file__)),'sha256':sha(__file__)}}
    (OUT/'processing.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'output':output,'maxDx':report['maxAppliedDxPixels'],'changedPixels':report['changedPixels'],'darkCentersUnchanged':report['allDarkCentersUnchanged'],'report':str(OUT/'processing.json')}))

if __name__=='__main__':main()

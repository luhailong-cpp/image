from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, json, hashlib, datetime, sys
R=Path(__file__).resolve().parent
B=R.parents[2]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p): return np.asarray(Image.open(p).convert('RGB'))
def path_cut(a,b,lo,hi,preferred,axis='x'):
    if axis=='y': a=a.transpose(1,0,2);b=b.transpose(1,0,2)
    a=a.astype(np.float32);b=b.astype(np.float32)
    error=np.sqrt(np.mean(np.minimum(abs(a-b),80)**2,axis=2))
    ga=np.gradient(a.mean(2),axis=1);gb=np.gradient(b.mean(2),axis=1)
    cost=error+np.minimum(abs(ga-gb),40)*.35+abs(np.arange(a.shape[1])-preferred)[None,:]*.035
    cost=cost[:,lo:hi];height,width=cost.shape;back=np.zeros((height,width),np.int8);dp=cost[0].copy()
    for y in range(1,height):
        choices=np.stack((np.r_[np.inf,dp[:-1]]+.6,dp,np.r_[dp[1:],np.inf]+.6))
        chosen=choices.argmin(0);dp=cost[y]+choices[chosen,np.arange(width)];back[y]=chosen-1
    path=np.empty(height,np.int32);path[-1]=int(dp.argmin())
    for y in range(height-1,0,-1): path[y-1]=path[y]+int(back[y,path[y]])
    return path+lo

def color_return(reference, moving, path, axis, support=160, cap=12):
    # Match only broad tone; no spatial smoothing of image pixels.
    a=reference.astype(np.float32);z=moving.astype(np.float32)
    if axis=='y': a=a.transpose(1,0,2);z=z.transpose(1,0,2)
    h,w=a.shape[:2]; profile=np.zeros((h,3),np.float32)
    for i,v in enumerate(path):
        lo=max(0,int(v)-24);hi=min(w,int(v)+25)
        aa=a[max(0,i-24):min(h,i+25),lo:hi];zz=z[max(0,i-24):min(h,i+25),lo:hi]
        residual=aa-zz;good=np.max(abs(residual),axis=2)<48
        if good.sum()>50: profile[i]=np.median(residual[good],axis=0)
    kernel=np.ones(49,np.float32)/49
    profile=np.stack([np.convolve(np.pad(profile[:,c],(24,24),mode='edge'),kernel,mode='valid') for c in range(3)],axis=1)
    profile=np.clip(profile,-cap,cap)
    distance=abs(np.arange(w)[None,:]-path[:,None]);weight=np.maximum(0,1-distance/support)**2
    field=profile[:,None,:]*weight[:,:,None]
    result=np.clip(np.rint(z+field),0,255).astype(np.uint8)
    if axis=='y': result=result.transpose(1,0,2);field=field.transpose(1,0,2)
    return result,field

def main(revision,paths):
    assert len(paths)==4
    D=R/('joint-'+revision);D.mkdir(exist_ok=True);Q=D/'qa';Q.mkdir(exist_ok=True)
    inputs=[Path(x) for x in paths];sources=[arr(x) for x in inputs]
    assert all(x.shape==(1254,1254,3) for x in sources)
    canvas=np.zeros((1254,4326,3),np.uint8);owner=np.zeros((1254,4326),np.uint8)
    canvas[:,:1254]=sources[0];owner[:,:1254]=1;cuts={};fields={}
    for i in range(1,4):
        x=i*1024;left=canvas[:,x:x+230];right=sources[i][:,:230]
        cut=path_cut(left,right,40,190,115)
        if revision!='v1':
            ref=sources[i].copy();ref[:,:230]=left
            sources[i],fields[f'segment{i+1}']=color_return(ref,sources[i],cut,'x')
            right=sources[i][:,:230];cut=path_cut(left,right,40,190,115)
        cuts[f'segment{i+1}']=cut
        take=np.arange(230)[None,:]>=cut[:,None]
        canvas[:,x:x+230]=np.where(take[:,:,None],right,left)
        owner[:,x:x+230]=np.where(take,i+1,owner[:,x:x+230])
        canvas[:,x+230:x+1254]=sources[i][:,230:];owner[:,x+230:x+1254]=i+1
    base_path=R/'references/north-joint-input-native.png';base=arr(base_path)
    upper=path_cut(base,canvas,90,420,260,'y')
    lower=path_cut(canvas,base,1120,1230,1180,'y')
    if revision!='v1':
        canvas,fields['upper']=color_return(base,canvas,upper,'y')
        canvas,fields['lower']=color_return(base,canvas,lower,'y')
    yy,xx=np.mgrid[:1254,:4326];mask=(yy>=upper[None,:])&(yy<lower[None,:])
    # Preserve far exterior context. Final tile starts at x115, inside this border.
    mask[:,:30]=False;mask[:,-30:]=False
    combined=np.where(mask[:,:,None],canvas,base)
    Image.fromarray(canvas).save(D/'native-quilt.png')
    Image.fromarray(owner).save(D/'source-owner.png')
    Image.fromarray(mask.astype(np.uint8)*255).save(D/'native-mask.png')
    Image.fromarray(combined).save(D/'joint-candidate.png')
    np.savez_compressed(D/'native-cuts.npz',upper=upper,lower=lower,**cuts)
    if fields: np.savez_compressed(D/'color-fields.npz',**fields)
    north_path=B/'tiles/current/r09_c12-candidate.png';south_path=B/'r10_c12/repairs/r10_c12-candidate-v5.png'
    north=arr(north_path).copy();south=arr(south_path).copy()
    assert np.array_equal(arr(B/'r10_c12/repairs/r10_c12-candidate-v2.png')[:627],south[:627])
    north[3469:]=combined[:627,115:4211];south[:627]=combined[627:,115:4211]
    north_file=D/'r09_c12-north-joint-candidate.png';south_file=D/'r10_c12-north-joint-candidate.png'
    Image.fromarray(north).save(north_file);Image.fromarray(south).save(south_file)
    for i in range(4):
        core=combined[:,115+i*1024:115+(i+1)*1024]
        Image.fromarray(core[467:787]).save(Q/f'shared-s{i+1}-native.png')
        # Entire return zones include the varying native ownership paths.
        Image.fromarray(core[:470]).save(Q/f'north-return-s{i+1}-native.png')
        Image.fromarray(core[1000:]).save(Q/f'south-return-s{i+1}-native.png')
    for i in range(1,4):
        x=115+i*1024
        Image.fromarray(combined[:,x-160:x+160]).save(Q/f'segment-junction-{i}-native.png')
    Image.fromarray(combined[:,115:4211]).resize((1638,502),Image.Resampling.LANCZOS).save(D/'preview.png')
    record={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'candidate_pending_native_visual_review','north':{'file':str(north_file),'sha256':sha(north_file)},'south':{'file':str(south_file),'sha256':sha(south_file)},'sourceImages':[{'file':str(p),'sha256':sha(p),'record':str(p)+'.generation.json'} for p in inputs],'baseJoint':{'file':str(base_path),'sha256':sha(base_path)},'sourceNorth':{'file':str(north_path),'sha256':sha(north_path)},'sourceSouth':{'file':str(south_path),'sha256':sha(south_path)},'operation':'Native same-coordinate binary ownership cuts across four AI repair segments and native outer returns. No resizing, displacement, feather, RGB correction or image blur in this operation. Earlier input corrections remain in provenance.','mask':{'file':str(D/'native-mask.png'),'sha256':sha(D/'native-mask.png')},'cuts':{'file':str(D/'native-cuts.npz'),'sha256':sha(D/'native-cuts.npz')},'globalJointOriginXY':[44941,36237],'sourceOwnerMap':str(D/'source-owner.png'),'qa':str(Q),'formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False}
    if fields:
        record['operation']='Native same-coordinate binary ownership cuts across four AI segments and outer returns, with additive RGB fields bounded12/channel per stage, spatial support160px and49px-smoothed profiles. No resizing, displacement, feather or image blur. Earlier input corrections remain in provenance.'
        record['colorFields']={'file':str(D/'color-fields.npz'),'sha256':sha(D/'color-fields.npz'),'actualMaxAbsPerField':{key:float(abs(value).max()) for key,value in fields.items()}}
    write(D/'record.json',record)
    for p in [north_file,south_file]:write(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':record['sourceImages']+[record['sourceNorth'],record['sourceSouth']],'operation':record['operation'],'fullOperationRecord':str(D/'record.json'),'formalAccepted':False})
    print(json.dumps(record))

if __name__=='__main__':main(sys.argv[1],sys.argv[2:])

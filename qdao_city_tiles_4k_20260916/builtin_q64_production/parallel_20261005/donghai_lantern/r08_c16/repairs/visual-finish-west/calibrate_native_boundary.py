from pathlib import Path
import numpy as np, json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def write(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for i in range(1,5):
    sp=B/'native'/f's{i}.png';tp=B/'guides'/f's{i}-actual-pair.png'
    n=np.array(Image.open(sp).convert('RGB')).astype(np.float32);t=np.array(Image.open(tp).convert('RGB')).astype(np.float32)
    # Corresponding native-left vs actual immutable c15 pixels; these are residual colors, not transferred texture.
    boundaryColor=np.median(n[:,622:627],axis=1)
    residual=np.clip(np.median(t[:,622:627]-n[:,622:627],axis=1),-24,24)
    target=n[:,627:977]
    num=np.zeros_like(target);den=np.zeros(target.shape[:2],np.float32)
    sigma=4+np.arange(350,dtype=np.float32)*.40
    for dy in range(-144,145):
        yy=np.arange(1254);sy=np.clip(yy+dy,0,1253)
        colors=boundaryColor[sy,None,:]
        colorDist=np.mean((target-colors)**2,axis=2)
        weight=np.exp(-colorDist/(2*14**2)-dy**2/(2*sigma[None,:]**2))
        num+=weight[:,:,None]*residual[sy,None,:];den+=weight
    delta=np.clip(num/np.maximum(den[:,:,None],1e-9),-24,24)
    out=n.astype(np.uint8);out[:,627:977]=np.clip(np.rint(target+delta),0,255).astype(np.uint8)
    # Only actual correction fields are smoothed/transported; image pixels are never blurred or warped.
    p=B/'calibrated-boundary'/f's{i}.png';p.parent.mkdir(exist_ok=True);Image.fromarray(out).save(p)
    fp=p.with_name(f's{i}-field.npz');np.savez_compressed(fp,offsetRight350=delta,boundarySameCoordinateResidual=residual,boundaryNativeRGB=boundaryColor)
    rec={'operation':'Bounded same-coordinate c15/native-left RGB residual transport into right strip using continuous native-RGB similarity and smooth spatial falloff; no texture transfer, image blur, warp or resampling','derivedFrom':[ref(sp),ref(tp)],'field':ref(fp),'maxAbsRGBField':float(np.abs(delta).max()),'samplePairRect':[622,0,627,1254],'fieldAppliedPairRect':[627,0,977,1254],'colorSimilaritySigma':14,'spatialSigmaAtX0':4,'spatialSigmaGrowthPerPixel':.40,'immutableC15UsedOnlyAsEvidence':True,'visualReview':'pending'}
    write(Path(str(p)+'.generation.json'),{**ref(p),**rec})
    print(json.dumps({'id':i,'max':rec['maxAbsRGBField'],'borderMedianAbsBefore':np.median(np.abs(t[:,626]-n[:,627]),axis=0).tolist(),'borderMedianAbsAfter':np.median(np.abs(t[:,626]-out[:,627]),axis=0).tolist()}))


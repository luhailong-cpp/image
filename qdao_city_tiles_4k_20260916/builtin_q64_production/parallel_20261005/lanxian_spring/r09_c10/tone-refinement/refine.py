"""Native pixel tone-only correction; read-only selected inputs, bounded additive RGB."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
TILE=OUT.parent
H=115; N=4326; RADIUS=320; LIMIT=16
EXPECTED={'core4096.png':'26275b5d8e0eb210501f97e57a9aa39eae5696c3974f5f5e0dadd8fdae15224f','extended4326.png':'a6b1616c59abe7a307500ecccca1c2bf428a8b83e0edc673a580550b1315eab9'}
MATERIALS=['excluded','water','gray_stone_or_shadow','green','warm_paving']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(t):
    t=np.clip(t,0,1); return t*t*(3-2*t)
def labels(a):
    z=a.astype(np.int16); r,g,b=z[...,0],z[...,1],z[...,2]
    c=np.zeros(z.shape[:2],np.uint8)
    c[(b>g+8)&(g>r+14)]=1
    c[(np.abs(r-g)<26)&(b>=g-12)&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<45)]=2
    c[(g>r+5)&(g>b+10)]=3
    c[(r>=g+4)&(g>b+8)&(r-g<50)&(r>90)]=4
    return c
def interpolate(nodes,values):
    x=np.arange(N)
    j=np.searchsorted(nodes,x,side='right')-1; j=np.clip(j,0,len(nodes)-2)
    t=smooth((x-nodes[j])/(nodes[j+1]-nodes[j]))
    return values[j]*(1-t[:,None])+values[j+1]*t[:,None]
def estimate(a,c,seam):
    # Estimate RGB steps only from low-gradient pixels of the same material.
    left=a[:,seam-3:seam].mean(axis=1)
    right=a[:,seam:seam+3].mean(axis=1)
    delta=right-left
    gleft=np.max(np.abs(np.diff(a[:,seam-5:seam],axis=1)),axis=(1,2))
    gright=np.max(np.abs(np.diff(a[:,seam:seam+5],axis=1)),axis=(1,2))
    valid=(gleft<7)&(gright<7)&(np.max(np.abs(delta),axis=1)<32)
    same=np.all(c[:,seam-3:seam+3]==c[:,seam:seam+1],axis=1)
    nodes=np.r_[0,np.arange(64,N-64,64),N-1].astype(int)
    profile=np.zeros((N,5,3),np.float32); notes={}
    for m in range(1,5):
        values=[]; counts=[]
        for p in nodes:
            lo=max(0,p-96); hi=min(N,p+97)
            ok=valid[lo:hi]&same[lo:hi]&(c[lo:hi,seam]==m)
            ds=delta[lo:hi][ok]
            counts.append(len(ds))
            values.append(np.median(ds,axis=0) if len(ds)>=12 else np.full(3,np.nan))
        values=np.array(values,dtype=np.float32)
        good=np.isfinite(values[:,0])
        if not good.any(): continue
        for i,p in enumerate(nodes):
            if not good[i]:
                distances=np.abs(nodes[good]-p); j=int(np.argmin(distances))
                values[i]=values[good][j] if distances[j]<=192 else 0
        # Retain measured local hue offsets, prevent uncertain colorful casts.
        lum=values.mean(axis=1,keepdims=True)
        chroma=values-lum
        cap=4 if m in [2,4] else (16 if m==1 else 8)
        values=np.clip(lum+np.clip(chroma,-cap,cap),-LIMIT*2,LIMIT*2)
        values[np.max(np.abs(values),axis=1)<.75]=0
        profile[:,m]=interpolate(nodes,values)
        notes[MATERIALS[m]]={'nodes':nodes.tolist(),'rightMinusLeftRGB':np.round(values,4).tolist(),'sampleCounts':counts}
    return profile,notes

def main():
    (OUT/'qa').mkdir(exist_ok=True)
    for f,h in EXPECTED.items(): assert sha(TILE/'selected'/f)==h,(f,'unexpected mutation')
    src=np.array(Image.open(TILE/'selected/extended4326.png').convert('RGB'))
    surface=np.array(Image.open(TILE/'selected/surface-mask4326.png').convert('L'))
    classes=labels(src); classes[surface>0]=0
    field=np.zeros(src.shape,np.float32); manifest=[]
    allowed=np.zeros(src.shape[:2],bool)
    for axis in ['vertical','horizontal']:
        # Second axis measures the first-axis-corrected color, not duplicate cross bias.
        work=src.astype(np.float32)+field
        if axis=='horizontal': work=work.transpose(1,0,2); cl=classes.T
        else: cl=classes
        for core_seam in [1024,2048,3072]:
            s=H+core_seam
            prof,notes=estimate(work,cl,s)
            x=np.arange(s-RADIUS,s+RADIUS)
            distance=np.abs(x-(s-.5))
            weight=1-smooth(distance/RADIUS)
            sign=np.where(x<s,1.,-1.)*.5
            correction=prof[np.arange(N)[:,None],cl[:,x]]*(weight*sign)[None,:,None]
            if axis=='vertical':
                field[:,x]+=correction
                allowed[:,x]=True
            else:
                field[x,:]+=correction.transpose(1,0,2)
                allowed[x,:]=True
            manifest.append({'axis':axis,'coreSeam':core_seam,'extendedSeam':s,'normalSupportPixelsEitherSide':RADIUS,'profile':notes})
    # Freeze accepted north interface (115px halo + first64 core rows), then
    # smoothly enter full correction over256 core rows. No north-guide mutation.
    north_weight=smooth((np.arange(N)-(H+64))/256)
    field*=north_weight[:,None,None]
    field[classes==0]=0
    field=np.clip(field,-LIMIT,LIMIT)
    dst=np.clip(np.rint(src.astype(np.float32)+field),0,255).astype(np.uint8)
    diff=dst.astype(np.int16)-src.astype(np.int16)
    changed=np.any(diff!=0,axis=2)
    assert not np.any(changed&~allowed)
    assert not np.any(changed&(surface>0))
    assert np.max(np.abs(diff))<=LIMIT
    np.savez_compressed(OUT/'additive-rgb-field4326.npz',field=field)
    np.savez_compressed(OUT/'actual-rgb-delta4326.npz',delta=diff.astype(np.int8))
    Image.fromarray(classes).save(OUT/'material-labels4326.png')
    Image.fromarray((allowed*255).astype(np.uint8)).save(OUT/'allowed-support4326.png')
    Image.fromarray((changed*255).astype(np.uint8)).save(OUT/'changed-mask4326.png')
    Image.fromarray(dst).save(OUT/'extended4326.png')
    core=Image.fromarray(dst[H:H+4096,H:H+4096])
    core.save(OUT/'core4096.png'); core.resize((1254,1254),Image.Resampling.LANCZOS).save(OUT/'preview1254.png')
    boxes=json.loads((OUT/'qa/boxes.json').read_text())
    for k,v in boxes.items(): core.crop(v).save(OUT/'qa'/f'{k}-after.png')
    border=np.ones(src.shape[:2],bool); border[H:H+4096,H:H+4096]=False
    stats={'changedPixels':int(changed.sum()),'changedCorePixels':int(changed[H:H+4096,H:H+4096].sum()),'changedHaloPixels':int((changed&border).sum()),'maxAbsActualRGBPerChannel':np.max(np.abs(diff),axis=(0,1)).tolist(),'outsideAllowedSupportExact':bool(np.array_equal(dst[~allowed],src[~allowed])),'excludedMaterialsAndSeasonalMaskExact':bool(np.array_equal(dst[classes==0],src[classes==0])),'coreExactExtendedCenter':bool(np.array_equal(np.array(Image.open(OUT/'core4096.png')),dst[H:H+4096,H:H+4096]))}
    processing={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'bounded additive RGB tone-only correction at unchanged pixel coordinates','source':EXPECTED,'sourceDirectory':str(TILE/'selected'),'sourceChainFinding':'Pinned day selection-proof confirms all16 native mappings exact; postAssemblyToneApplied=false. Correcting raw patch bias, not reversing old fields.','geometry':{'warp':None,'shift':[0,0],'resampling':None,'blurImage':False,'upscale':False,'coreBoxExtendedLTRB':[H,H,H+4096,H+4096]},'limits':{'cumulativeMaxPerChannel':LIMIT,'radiusEitherSideEachInternal1024GridSeam':RADIUS,'outsideSupport':'byte exact','outwardHalo':'Correction continues into west/east/south115halo; north115halo and first64core rows exact unchanged. Refresh changed neighboring guide strips.'},'method':{'seamSampleWidthEachSide':3,'alongSeamNodeSpacing':64,'alongSeamSampleHalfWindow':96,'minimumSameMaterialSamples':12,'sameMaterialSixPixelsRequired':True,'withinSideGradientMaxExclusive':7,'rawDifferenceMaxExclusive':32,'nearestFallbackMaxDistance':192,'fieldInterpolation':'piecewise cubic smoothstep; fields only','normalTaper':'symmetric half-bias x (1-smoothstep(distance/320))','northBoundary':'zero y<=179 extended, smoothstep to full at435 extended','materials':MATERIALS,'seasonalSourceEntityMasksExcluded':True,'tinyBiasCutoff':.75,'neutralChromaDeviationCap':4,'otherChromaDeviationCap':8,'twoAxes':'vertical first; horizontal estimates from virtual vertical-corrected pixels'},'profiles':manifest,'statistics':stats,'outputs':{f:sha(OUT/f) for f in ['core4096.png','extended4326.png','preview1254.png','additive-rgb-field4326.npz','actual-rgb-delta4326.npz','material-labels4326.png','allowed-support4326.png','changed-mask4326.png']},'formalAccepted':False,'visualQA':'pending'}
    processing['method']['otherChromaDeviationCap']={'water':16,'green':8}
    write(OUT/'processing.json',processing)
    for f in ['core4096.png','extended4326.png','preview1254.png']:
        write(OUT/(f+'.generation.json'),{'file':str(OUT/f),'sha256':sha(OUT/f),'derivedFrom':[{'file':str(TILE/'selected'/'extended4326.png'),'sha256':EXPECTED['extended4326.png'],'generationRecord':str(TILE/'selected'/'extended4326.png.generation.json')}],'operation':processing['operation']+('; preview downsample only' if f.startswith('preview') else ''),'processingRecord':str(OUT/'processing.json'),'newAIGeneration':False,'actualModel':None,'actualQuality':None,'modelEvidence':'Inherited source chain; no new model call or reassignment.'})
    print(json.dumps({'statistics':stats,'outputs':processing['outputs']},indent=2))
if __name__=='__main__': main()

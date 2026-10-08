"""Bounded RGB-difference correction of r07_c15 overlap tonal steps.
Keeps the accepted geometry's original two-pixel seam masks and all source pixels
outside the 230-pixel overlaps; low-pass filtering is applied only to RGB differences.
"""
from pathlib import Path
import hashlib
import io
import json
import numpy as np
from PIL import Image
import assembly_r07_c15 as a

ROOT=Path(__file__).resolve().parent
DEST=a.TILE/'repairs'/'unified'/'precolor'
MASKS=a.MASKS
BASE=a.OUT/'r07_c15.png'
BASE_EXT=a.OUT/'extended-context.png'
EXPECTED='3d6784d05e08447095081e0a2c425a1d11b2f7c461a7ff1dd74d9efa7644ea13'
CAP=32
infos=[]
def lowpass(v):
    for _ in range(3):
        for axis in (0,1):
            pad=[(0,0),(0,0)];pad[axis]=(24,24)
            p=np.pad(v,pad,mode='reflect')
            c=np.cumsum(p,axis=axis,dtype=np.float64)
            z=np.take(c,[0],axis=axis)*0
            c=np.concatenate((z,c),axis=axis)
            v=(c[49:]-c[:-49])/49 if axis==0 else (c[:,49:]-c[:,:-49])/49
    return v.astype(np.float32)
def category(x):
    x=x.astype(np.int16)
    return np.where((x[:,:,2]>x[:,:,0]+15)&(x[:,:,1]>x[:,:,0]+5),1,
        np.where((x[:,:,0]>x[:,:,2]+15)&(x[:,:,0]>x[:,:,1]+4),2,0))
def append(base,incoming,label,orientation):
    l,r=base[:,-230:],incoming[:,:230]
    with np.load(MASKS/(label+'.npz')) as saved:
        alpha=saved['alpha_u8'].copy()
        rect=saved['overlap_rect_extended_xywh'].copy()
    if orientation=='horizontal':alpha=alpha.T
    raw=a.blend(l,r,alpha)
    cl,cr=category(l),category(r)
    delta=l.astype(np.float32)-r.astype(np.float32)
    field=np.zeros_like(delta)
    denominator=np.zeros(delta.shape[:2],dtype=np.float32)
    for c in (0,1,2):
        valid=((cl==c)&(cr==c)).astype(np.float32)
        den=lowpass(valid)
        denominator+=den
        for k in range(3):
            field[:,:,k]+=lowpass(delta[:,:,k]*valid)
    # Continuous normalized confidence avoids threshold speckles at dark wood.
    field/=np.maximum(denominator[:,:,None],0.001)
    field=np.clip(field,-CAP,CAP)
    linear=np.linspace(0,1,230,dtype=np.float32)[None,:,None]
    # Smooth low-frequency tonal transition, original hard texture selection.
    correction=(alpha[:,:,None].astype(np.float32)/255-linear)*field
    corrected=np.clip(np.rint(raw.astype(np.float32)+correction),0,255).astype(np.uint8)
    delta_actual=corrected.astype(np.int16)-raw.astype(np.int16)
    fp=a.writable(DEST/'fields'/(label+'.npz'))
    np.savez_compressed(fp,field_rgb_f16=field.astype(np.float16),
                       correction_rgb_i16=delta_actual,
                       rect_extended_xywh=rect,orientation=np.asarray(orientation),
                       material_agreement_u8=(cl==cr).astype(np.uint8))
    infos.append({'id':label,'orientation':orientation,'overlapRectExtendedXYWH':rect.tolist(),
                  'originalAlphaFile':str(MASKS/(label+'.npz')),
                  'originalAlphaSha256':a.sha(MASKS/(label+'.npz')),
                  'differenceField':str(fp),'differenceFieldSha256':a.sha(fp),
                  'maxAppliedChannelChange':int(np.abs(delta_actual).max())})
    return np.concatenate((base[:,:-230],corrected,incoming[:,230:]),axis=1)
def main():
    arrays,entries,missing=a.load_sources()
    a.require(not missing,'Missing source')
    def raw_append(base,incoming,label,orientation):
        with np.load(MASKS/(label+'.npz')) as saved:
            alpha=saved['alpha_u8'].copy()
        if orientation=='horizontal':alpha=alpha.T
        mixed=a.blend(base[:,-230:],incoming[:,:230],alpha)
        return np.concatenate((base[:,:-230],mixed,incoming[:,230:]),axis=1)
    raw_rows=[]
    for row in range(1,5):
        merged=arrays[row,1]
        for col in range(2,5):
            merged=raw_append(merged,arrays[row,col],f'vertical_r{row:02d}_c{col-1:02d}_c{col:02d}','vertical')
        raw_rows.append(merged)
    baseline=raw_rows[0]
    for row in range(2,5):
        baseline=raw_append(baseline.transpose(1,0,2),raw_rows[row-1].transpose(1,0,2),
                            f'horizontal_r{row-1:02d}_r{row:02d}','horizontal').transpose(1,0,2)
    check=io.BytesIO();Image.fromarray(baseline[115:4211,115:4211]).save(check,format='PNG')
    a.require(hashlib.sha256(check.getvalue()).hexdigest()==EXPECTED,'Reproduced baseline mismatch')
    extcheck=io.BytesIO();Image.fromarray(baseline).save(extcheck,format='PNG')
    rows=[]
    for row in range(1,5):
        merged=arrays[row,1]
        for col in range(2,5):
            merged=append(merged,arrays[row,col],f'vertical_r{row:02d}_c{col-1:02d}_c{col:02d}','vertical')
        rows.append(merged)
    merged=rows[0]
    for row in range(2,5):
        merged=append(merged.transpose(1,0,2),rows[row-1].transpose(1,0,2),
                      f'horizontal_r{row-1:02d}_r{row:02d}','horizontal').transpose(1,0,2)
    change=np.clip(merged.astype(np.int16)-baseline.astype(np.int16),-CAP,CAP)
    # Upper halo and first 128 final rows are retained; southern reference is read-only.
    change[:243]=0
    merged=np.clip(baseline.astype(np.int16)+change,0,255).astype(np.uint8)
    union=np.zeros(baseline.shape[:2],dtype=bool)
    for p in (1024,2048,3072):
        union[:,p:p+230]=True
        union[p:p+230,:]=True
    a.require(np.array_equal(merged[~union],baseline[~union]),'Pixels changed outside overlap union')
    a.require(np.array_equal(merged[:243],baseline[:243]),'Protected north changed')
    diff=merged.astype(np.int16)-baseline.astype(np.int16)
    fp=a.writable(DEST/'fields'/'final-correction.npz')
    np.savez_compressed(fp,correction_rgb_i16=diff,allowed_mask_u8=union.astype(np.uint8),
                       changed_mask_u8=np.any(diff!=0,axis=2).astype(np.uint8))
    ext=Image.fromarray(merged)
    final=ext.crop((115,115,4211,4211))
    out=a.save_image(DEST/'candidate.png',final)
    extinfo=a.save_image(DEST/'extended-context.png',ext)
    a.QA=DEST/'qa';a.ART=DEST/'candidate.png'
    north,ni=a.checked_south()
    qa=a.write_qa(final,ext,north)
    manifest={'createdAtUtc':a.utc_now(),'tile':'r07_c15','status':'candidate-pending-visual-review',
      'baseline':{'historicalFile':str(BASE),'sha256':EXPECTED,'extendedSha256':hashlib.sha256(extcheck.getvalue()).hexdigest(),
                  'reproduction':'Original native inputs and fixed recorded seam alpha masks; no original raster backup required'},
      'candidate':out,'extendedContext':extinfo,'nativeSources':entries,
      'method':'Fixed original DP texture masks plus material-agreement-weighted continuous low-frequency RGB difference compensation inside original 230px overlaps. Difference field only: three 49px separable box passes, normalized continuously to avoid material-threshold speckles. Spatial image pixels never blurred or resampled.',
      'maxPerChannelCorrection':int(np.abs(diff).max()),'cap':CAP,
      'topHaloAndCore128Unchanged':True,'outsideOverlapUnionUnchanged':True,
      'imageResampling':False,'imageBlur':False,'geometryWarp':False,
      'finalCorrection':{'file':str(fp),'sha256':a.sha(fp)},
      'fields':infos,'qa':qa,'script':{'file':str(Path(__file__)),'sha256':a.sha(__file__)},
      'visualReview':'pending','formalAccepted':False}
    a.save_json(DEST/'manifest.json',manifest)
    a.save_json(a.QA/'manifest.json',{'candidateSha256':out['sha256'],'qa':qa,'visualReview':'pending'})
    print(json.dumps({'candidate':out,'top128Unchanged':True,'correctionCap':int(np.abs(diff).max())},indent=2))
if __name__=='__main__':main()


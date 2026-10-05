"""Bounded RGB-only matching for visually identified existing-structure seam bands."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];T=ROOT/'r08_c09';O=T/'tone-v2';O.mkdir(exist_ok=True)
vendor=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
sys.path.insert(0,str(vendor));import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=T/'candidate/extended4326.png';a=np.array(Image.open(source).convert('RGB'));original=a.copy();notes=[]
def match(axis,k,segments=None):
    global a
    b=a.transpose(1,0,2) if axis=='x' else a
    l=b[k-16:k].transpose(1,0,2).astype(np.float32);r=b[k:k+16].transpose(1,0,2).astype(np.float32)
    lm=np.median(l[:,-5:-1],axis=1);rm=np.median(r[:,1:5],axis=1)
    sl=np.median(np.diff(l[:,-15:-5],axis=1),axis=1);sr=np.median(np.diff(r[:,5:15],axis=1),axis=1)
    jump=rm-lm-3*(sl+sr)
    variation=np.maximum(np.max(np.std(l[:,-15:-5],axis=1),axis=1),np.max(np.std(r[:,5:15],axis=1),axis=1))
    valid=(variation<6)&(np.max(np.abs(jump),axis=1)<30);idx=np.flatnonzero(valid)
    assert len(idx)>100,(axis,k,len(idx))
    vals=np.stack([np.interp(np.arange(len(b[0])),idx,jump[idx,c]) for c in range(3)],axis=1).astype(np.float32)
    vals=cv2.medianBlur(vals.reshape(-1,1,3),5).reshape(-1,3);vals=cv2.GaussianBlur(vals,(1,0),sigmaX=0,sigmaY=5);vals=np.clip(vals,-24,24)
    longitudinal=np.ones(len(vals),np.float32)
    if segments:
        longitudinal[:]=0
        for start,end in segments:
            coords=np.arange(len(vals));dist=np.maximum(start-coords,coords-end)
            longitudinal=np.maximum(longitudinal,np.clip(1-dist/96,0,1))
    d=np.arange(-192,192,dtype=np.float32)+.5;t=np.clip(1-np.abs(d)/192,0,1);t=t*t*(3-2*t);signed=np.where(d<0,.5,-.5)*t
    field=(vals[:,None,:]*signed[None,:,None]*longitudinal[:,None,None]).transpose(1,0,2).astype(np.float32)
    b[k-192:k+192]=np.rint(np.clip(b[k-192:k+192].astype(np.float32)+field,0,255)).astype(np.uint8)
    name=f'{axis}{k-115}';fp=O/f'{name}-correction.npy';np.save(fp,field)
    mask=np.uint8(np.clip(np.abs(signed[:,None])*2*longitudinal[None,:],0,1)*255);mp=O/f'{name}-mask.png';Image.fromarray(mask).save(mp)
    notes.append({'axis':axis,'coordinateInCore':k-115,'bandRadius':192,'validSampleCount':int(valid.sum()),'maxAbsoluteCorrectionRGB':np.abs(field).max(axis=(0,1)).tolist(),'correctionField':str(fp),'correctionFieldSha256':sha(fp),'mask':str(mp),'maskSha256':sha(mp),'longitudinalSegmentsInExtended':segments,'resampling':'none','geometricShift':0})
    a=b.transpose(1,0,2) if axis=='x' else b
for y in [1024,2048,3072]:match('y',y+115)
# Only the reported first vertical seam's two material transition regions.
match('x',1024+115,[(115,635),(1459,1819)])
ef=O/'extended4326.png';cf=O/'core4096.png';pf=O/'preview1024.png'
Image.fromarray(a).save(ef);Image.fromarray(a[115:4211,115:4211]).save(cf);Image.fromarray(a[115:4211,115:4211]).resize((1024,1024),Image.Resampling.LANCZOS).save(pf)
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'derivedFrom':{'file':str(source),'sha256':sha(source)},'operation':'Bounded RGB addition in inspected seam bands; original raster is never blurred, resized, warped or replaced with guide pixels. Correction field interpolated only from low-gradient seam samples. No missing structures repaired.','maxPerPassAbsoluteRGB':12,'maxCumulativeRGB':np.abs(a.astype(np.int16)-original.astype(np.int16)).max(axis=(0,1)).tolist(),'nativeDimensionsMaintained':[4326,4326],'seams':notes,'outputs':{k:{'file':str(p),'sha256':sha(p)} for k,p in [('extended',ef),('core',cf),('preview',pf)]},'formalAccepted':False,'visualRecheckRequired':True}
(O/'processing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(cf),'sha256':sha(cf),'maxCorrection':report['maxCumulativeRGB']}))

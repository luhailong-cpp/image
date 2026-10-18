"""Exact native pixel seam selection, no resizing, generated detail or blur."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image
from datetime import datetime,timezone
import produce as p

def join(a,b,label,records):
    overlap=230
    aa=a[:,-overlap:].astype(np.float32);bb=b[:,:overlap].astype(np.float32)
    costs=np.mean((aa-bb)**2,axis=2)
    h,w=costs.shape;dp=costs[0].copy();back=np.zeros((h,w),np.int8)
    for y in range(1,h):
        choices=np.stack([np.r_[np.inf,dp[:-1]],dp,np.r_[dp[1:],np.inf]])
        idx=choices.argmin(axis=0);back[y]=idx-1;dp=costs[y]+np.min(choices,axis=0)
    x=int(dp.argmin());path=np.empty(h,np.int16)
    for y in range(h-1,-1,-1):path[y]=x;x+=int(back[y,x])
    mask=np.arange(w)[None,:]>=path[:,None]
    mixed=np.where(mask[:,:,None],b[:,:overlap],a[:,-overlap:])
    out=np.concatenate([a[:,:-overlap],mixed,b[:,overlap:]],axis=1)
    records.append({'id':label,'overlap':overlap,'meanAbsDifference':float(np.mean(np.abs(aa-bb))),'seamMeanSquaredError':float(np.mean(costs[np.arange(h),path])),'cutPositions':path.tolist(),'everyOutputPixelFromOneNativeSource':True})
    return out

def main(t):
    d=p.OUT/t;sel=p.read(d/'selected.json');assert len(sel)==16;records=[];rows=[]
    for r in range(1,5):
        row=None
        for c in range(1,5):
            key=f'p{r:02d}_{c:02d}';n=sel[key];src=Path(n['source']['path']);assert p.sha(src)==n['source']['sha256']
            im=Image.open(src).convert('RGB');assert im.size==(1254,1254);a=np.asarray(im)
            row=a if row is None else join(row,a,f'row{r}-col{c}',records)
        rows.append(row)
    a=rows[0]
    for i,b in enumerate(rows[1:],2):a=join(a.transpose(1,0,2),b.transpose(1,0,2),f'rowjoin{i}',records).transpose(1,0,2)
    assert a.shape==(4326,4326,3)
    ver=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');qa=d/'qa'/('native-seam-'+ver);qa.mkdir(parents=True)
    context=Image.fromarray(a);final=context.crop((115,115,4211,4211));dest=d/'candidate'/f'{t}-4k-native-seam-{ver}.png';ct=d/'candidate'/f'{t}-context-native-seam-{ver}.png';p.png(dest,final);p.png(ct,context)
    p.png(qa/'overview-preview-only.png',final.resize((1024,1024),Image.Resampling.LANCZOS))
    for axis in ['x','y']:
        for pos in [1024,2048,3072]:
            for k in range(4):
                box=[pos-192,k*1024,pos+192,(k+1)*1024] if axis=='x' else [k*1024,pos-192,(k+1)*1024,pos+192]
                p.png(qa/f'{axis}{pos}-segment{k+1}-100pct.png',final.crop(box))
    n=p.read(p.OLD/('r13_c'+t[5:7])/'candidate/latest-assembly.json');south=Image.open(n['candidate']['path']).convert('RGB');joint=Image.new('RGB',(4096,512));joint.paste(final.crop((0,3840,4096,4096)));joint.paste(south.crop((0,0,4096,256)),(0,256));p.png(qa/'south-external-joint-100pct.png',joint)
    m={'createdAt':p.now(),'tile':t,'candidate':p.info(dest),'context':p.info(ct),'uniqueCoreCount':16,'sources':list(sel.values()),'composition':'Minimum-error path selects exact native pixels in230px overlaps. No resizing, warping, feather, blur, color matching, synthetic pixels or layout pixels. Output4096 is crop of4326 native assembly.','seams':records,'qaDirectory':str(qa),'internalQA':'pending_visual_review','externalQA':'pending','formalAccepted':False}
    p.write(d/'candidate'/f'{t}-native-seam-{ver}.manifest.json',m,True);p.write(d/'candidate/latest.json',m)
    print(__import__('json').dumps({'candidate':str(dest),'qa':str(qa),'formalAccepted':False}))
if __name__=='__main__':main(sys.argv[1])

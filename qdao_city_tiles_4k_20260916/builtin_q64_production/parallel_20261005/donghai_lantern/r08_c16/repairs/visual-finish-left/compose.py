from pathlib import Path
import json, hashlib, datetime
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'approved-sync/output/r08_c16.png'
EXT=ROOT.parent/'approved-sync/output/extended-context.png'
NAMES=['rail','inner-board','outer-board','lower-wood']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def desc(p):
    r={'file':str(p),'sha256':sha(p)}
    if str(p).endswith('.png'): r['pixels']=list(Image.open(p).size)
    return r
def save(p,a,record):
    Image.fromarray(a).save(p)
    r={**desc(p),**record}
    write(str(p)+'.generation.json',r)
    return r
def smooth(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

assert sha(BASE)=='7d821e83179cae126dd4e0f1be7f6b83f6a762bfe7b0f0caa4bfa3ec8de0bb22'
assert sha(EXT)=='7a6c1c38892ca9a35f3b433b27b960660af00d9415df37f2f72304efe52a4cb6'
base=np.array(Image.open(BASE).convert('RGB'));core=base.copy()
union=np.zeros((4096,4096),bool);patches=[]
out=ROOT/'output';out.mkdir(exist_ok=True)
qa=ROOT/'qa';qa.mkdir(exist_ok=True)
for name in NAMES:
    d=ROOT/name;prep=json.loads((d/'prepared.json').read_text(encoding='utf-8'))
    nr=json.loads((d/'native.png.generation.json').read_text(encoding='utf-8'))
    assert sha(d/'native.png')==nr['sha256']
    for ref in prep['references']: assert sha(ref['file'])==ref['sha256']
    native=np.array(Image.open(d/'native.png').convert('RGB'));assert native.shape==(1254,1254,3)
    x0,y0,x1,y1=prep['windowXYXY'];l,t,r,b=prep['roisXYXY'][0]
    yy,xx=np.mgrid[y0:y1,x0:x1]
    fade=32 if name=='outer-board' else 48
    a=np.minimum.reduce([smooth((xx-l)/fade),smooth((r-1-xx)/fade),smooth((yy-t)/fade),smooth((b-1-yy)/fade)])
    a=np.rint(a*255).astype(np.uint8)
    assert not np.any(a[(xx<350)|(xx>=1421)])
    support=a>0
    assert not np.any(union[y0:y1,x0:x1]&support)
    union[y0:y1,x0:x1]|=support
    c=base[y0:y1,x0:x1].astype(np.uint32);aa=a.astype(np.uint32)[...,None]
    result=((native.astype(np.uint32)*aa+c*(255-aa)+127)//255).astype(np.uint8)
    assert np.array_equal(result[~support],c.astype(np.uint8)[~support])
    core[y0:y1,x0:x1]=np.where(support[...,None],result,core[y0:y1,x0:x1])
    mask=save(d/'mask.png',a,{'operation':'explicit bounded smoothstep alpha; no DAY repair mask reused','windowXYXY':prep['windowXYXY'],'roisXYXY':prep['roisXYXY'],'featherPixels':fade,'allowedMaskTileXYXY':[350,0,1421,4096],'noArtworkFiltering':True})
    patched=save(d/'patched-window.png',result,{'operation':'integer alpha blend of local builtin native into fixed exact base crop','derivedFrom':[desc(BASE),desc(d/'native.png'),desc(d/'mask.png')],'windowXYXY':prep['windowXYXY'],'maskOutsideExact':True})
    patch={'name':name,'base':desc(BASE),'native':desc(d/'native.png'),'generationRecord':desc(d/'native.png.generation.json'),'mask':mask,'windowXYXY':prep['windowXYXY'],'roisXYXY':prep['roisXYXY'],'patchedWindow':patched,'blend':'(native * alpha + base * (255-alpha) + 127) // 255','sourceResampled':False,'actualModel':None,'actualQuality':None,'visualReview':'pending','daySyncRequired':False,'mechanicalColorFieldApplied':False}
    patches.append(patch)
diff=np.any(core!=base,axis=2)
assert not np.any(diff&~union)
assert not np.any(diff[:,:350]);assert not np.any(diff[:,1421:])
coredesc=save(out/'r08_c16.png',core,{'operation':'four disjoint locally generated paint repairs with exact alpha masks','derivedFrom':[desc(BASE)]+[p['native'] for p in patches]+[p['mask'] for p in patches],'actualModel':None,'actualQuality':None,'sourceResampled':False,'geometryChangeIntended':False,'formalAccepted':False})
ext=np.array(Image.open(EXT).convert('RGB'));oldext=ext.copy();ext[115:4211,115:4211]=core
assert np.array_equal(ext[:115],oldext[:115]);assert np.array_equal(ext[4211:],oldext[4211:]);assert np.array_equal(ext[:, :115],oldext[:, :115]);assert np.array_equal(ext[:,4211:],oldext[:,4211:])
extdesc=save(out/'extended-context.png',ext,{'operation':'replace exact core only; preserve all 115px true halo and corners','derivedFrom':[desc(EXT),coredesc],'coreRectXYXY':[115,115,4211,4211],'allHaloPixelsExact':True})
qaRows=[]
for patch in patches:
    name=patch['name'];l,t,r,b=patch['roisXYXY'][0]
    rects={'full1254':patch['windowXYXY'],'return-left':[l-112,t-96,l+112,b+96],'return-right':[r-112,t-96,r+112,b+96],'return-top':[l-96,t-112,r+96,t+112],'return-bottom':[l-96,b-112,r+96,b+112]}
    rows=[]
    for suffix,rect in rects.items():
        x0,y0,x1,y1=rect;assert 0<=x0<x1<=4096 and 0<=y0<y1<=4096
        row=save(qa/(name+'-'+suffix+'.png'),core[y0:y1,x0:x1],{'operation':'exact original-pixel final coherent candidate crop','derivedFrom':[coredesc],'tileRectXYXY':rect,'pixelScale':1,'resized':False,'visualReview':'pending'})
        rows.append(row);qaRows.append(row)
    patch['qa']=rows
    write(ROOT/name/'completion.json',patch)
ys,xs=np.where(diff)
manifest={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':desc(BASE),'baseExtended':desc(EXT),'candidate':coredesc,'extendedContext':extdesc,'patches':patches,'qa':qaRows,'proof':{'outsideUnionChangedPixels':int(np.count_nonzero(diff&~union)),'outsideAssignedDomainChangedPixels':int(np.count_nonzero(diff[:,:350])+np.count_nonzero(diff[:,1421:])),'changedPixels':int(diff.sum()),'actualChangedBoundsXYXY':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'alphaSupportsDisjoint':True,'trueHaloAllExact':True,'baseImmutable':True,'coreCropExact':True},'DAYWritten':False,'c15Written':False,'geometryChangeIntended':False,'registryWritten':False,'formalAccepted':False,'visualReview':'pending','script':desc(Path(__file__))}
write(out/'integration-manifest.json',manifest)
print(json.dumps({'candidate':coredesc['sha256'],'extended':extdesc['sha256'],'manifest':sha(out/'integration-manifest.json'),'qa':len(qaRows),'proof':manifest['proof']},ensure_ascii=False))

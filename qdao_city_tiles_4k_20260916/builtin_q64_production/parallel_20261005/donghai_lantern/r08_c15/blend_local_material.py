from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image

B = Path(__file__).resolve().parent / 'repairs/local-material-finish'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p): return {'file': str(p), 'sha256': sha(p)}
def js(p,j): p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save(p,im,extra):
    im.save(p);r={**ref(p),'pixels':list(im.size),**extra};js(Path(str(p)+'.generation.json'),r);return r
for name in ['wood-tone','blue-bevel','roof-tone']:
    d=B/name;q=d/'qa';q.mkdir(exist_ok=True);r=read(d/'prepared.json');n=read(d/'native.png.generation.json')
    assert sha(n['file'])==n['sha256'] and sha(r['source']['file'])==r['source']['sha256']
    box=r['cropXYXY'];roi=r['authorizedROI'];local=r['roiInNative']
    base=Image.open(r['source']['file']).convert('RGB').crop(box);arr=np.asarray(base).copy()
    incoming=np.asarray(Image.open(n['file']).convert('RGB'))
    mask=np.zeros((1254,1254),np.uint8);x,y,x1,y1=local;yy,xx=np.mgrid[y:y1,x:x1]
    feather=40 if name!='roof-tone' else 48
    t=np.clip(np.minimum.reduce([xx-x,x1-1-xx,yy-y,y1-1-yy])/feather,0,1)
    mask[y:y1,x:x1]=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
    m=save(d/'mask.png',Image.fromarray(mask),{'operation':'bounded local smoothstep alpha; no art filtering','windowXYXY':box,'roisXYXY':[roi],'featherPixels':feather})
    w=mask.astype(np.uint32)[...,None]
    out=((arr.astype(np.uint32)*(255-w)+incoming.astype(np.uint32)*w+127)//255).astype(np.uint8)
    assert np.array_equal(out[mask==0],arr[mask==0])
    patched=save(d/'patched-window.png',Image.fromarray(out),{'base':r['source'],'native':ref(d/'native.png'),'mask':m,'windowXYXY':box,'outsideMaskPixelIdentical':True,'sourceResampled':False,'imageBlur':False})
    qa=[save(q/'full1254.png',Image.fromarray(out),{'pixelScale':1,'resized':False,'source':patched})]
    pad=80
    crops={'left':[x-pad,y-pad,x+pad,y1+pad],'right':[x1-pad,y-pad,x1+pad,y1+pad],'top':[x-pad,y-pad,x1+pad,y+pad],'bottom':[x-pad,y1-pad,x1+pad,y1+pad]}
    for side,crop in crops.items():
        crop=[max(0,crop[0]),max(0,crop[1]),min(1254,crop[2]),min(1254,crop[3])]
        qa.append(save(q/(side+'.png'),Image.fromarray(out).crop(crop),{'source':patched,'cropInWindowXYXY':crop,'pixelScale':1,'resized':False}))
    js(d/'completion.json',{'base':r['source'],'native':ref(d/'native.png'),'mask':m,'windowXYXY':box,'patchedWindow':patched,'roisXYXY':[roi],'outsideMaskPixelIdentical':True,'geometryChangeAllowed':False,'qa':qa,'visualReview':'pending','formalAccepted':False})
    print(name,patched['sha256'])

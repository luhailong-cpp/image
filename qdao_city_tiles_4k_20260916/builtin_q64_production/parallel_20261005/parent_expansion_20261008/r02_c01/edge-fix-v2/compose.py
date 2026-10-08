from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib
from datetime import datetime,timezone
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=P.parent/'joined.png'
assert sha(base)=='c04e282abf2ab45e1da4779312db292274b7fa76c36b87efd79d8afb4ab0ad38'
a=Image.open(base).convert('RGB');b=Image.open(P/'native.png').convert('RGB')
assert a.size==b.size==(1254,1254)
regions=[('north-gray',(330,0,665,120),24),('north-left-bevel',(220,0,335,115),22),('north-right-bevel',(635,0,960,185),28),('west-bevel',(0,380,145,570),26),('southwest-bevel',(265,960,445,1170),28),('south-left-line',(495,1140,635,1254),28),('south-right-line',(925,1140,1075,1254),28)]
mask=np.zeros((1254,1254),np.uint8)
for name,(l,t,r,d),f in regions:
 y,x=np.mgrid[t:d,l:r]
 distances=[(x-l)/f,(r-1-x)/f]
 if t>0:distances.append((y-t)/f)
 if d<1254:distances.append((d-1-y)/f)
 if l==0:distances=distances[1:]
 z=np.clip(np.minimum.reduce(distances),0,1)
 z=z*z*(3-2*z)
 mask[t:d,l:r]=np.maximum(mask[t:d,l:r],np.round(z*255).astype(np.uint8))
assert np.max(mask[:,1100:])==0
maskim=Image.fromarray(mask);maskim.save(P/'local-mask.png')
joined=Image.composite(b,a,maskim);joined.save(P/'joined.png')
aa=np.array(a);bb=np.array(joined)
assert np.array_equal(aa[mask==0],bb[mask==0])
assert np.array_equal(aa[:,1100:],bb[:,1100:])
Q=P/'qa';Q.mkdir(exist_ok=True)
crops=[('north-return',(0,0,1254,280)),('west-return',(0,320,250,650)),('southwest-return',(200,880,520,1254)),('south-return',(430,1060,1100,1254)),('protected-east',(1100,0,1254,1254))]
qa=[]
for name,box in crops:
 p=Q/(name+'.png');joined.crop(box).save(p)
 qa.append({'file':str(p),'sha256':sha(p),'cropLTRB':box,'nativeScale':1,'actuallyViewed':False})
rec={'file':str(P/'joined.png'),'sha256':sha(P/'joined.png'),'width':1254,'height':1254,'operation':'Coordinate-identical composite of localized native AI repair regions with smoothstep alpha transition; no image resampling, registration, color correction or pixel blur. Right x>=1100 exactly unchanged.','derivedFrom':[{'file':str(base),'sha256':sha(base),'manifest':str(P.parent/'manifest.json')},{'file':str(P/'native.png'),'sha256':sha(P/'native.png'),'generationRecord':str(P/'native.png.generation.json')}],'mask':{'file':str(P/'local-mask.png'),'sha256':sha(P/'local-mask.png')},'regions':[{'name':n,'boundsLTRB':b,'alphaTransitionWidth':f} for n,b,f in regions]}
(P/'joined.png.generation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8')
m={'createdAt':datetime.now(timezone.utc).isoformat(),'file':str(P/'joined.png'),'sha256':sha(P/'joined.png'),'pixels':[1254,1254],'generationRecord':str(P/'joined.png.generation.json'),'source':rec['derivedFrom'][0],'native':rec['derivedFrom'][1],'mask':rec['mask'],'qa':qa,'proof':{'resampling':False,'registration':False,'nativePixelScale':1,'pixelsChanged':int(np.any(aa!=bb,axis=2).sum()),'outsideMaskExact':True,'rightAtAndBeyond1100Exact':True},'status':'pending_visual_review','formalAccepted':False}
(P/'manifest.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':m['file'],'sha256':m['sha256'],'proof':m['proof']}))


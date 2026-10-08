from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((P/'request.json').read_text(encoding='utf-8-sig'));a=Image.open(P/'context.png').convert('RGB');b=Image.open(P/'native.png').convert('RGB');assert a.size==b.size==(1254,1254)
m=np.zeros((1254,1254),np.uint8)
regions=[('upper-gold',(260,45,480,265),28),('west-brown',(200,350,415,630),30)]
for name,(l,t,r,d),f in regions:
 y,x=np.mgrid[t:d,l:r];z=np.clip(np.minimum.reduce([(x-l)/f,(r-1-x)/f,(y-t)/f,(d-1-y)/f]),0,1);z=z*z*(3-2*z);m[t:d,l:r]=np.maximum(m[t:d,l:r],np.round(z*255).astype(np.uint8))
mask=Image.fromarray(m);mask.save(P/'alpha-mask.png');joined=Image.composite(b,a,mask);joined.save(P/'joined.png');aa=np.array(a);jj=np.array(joined);diff=np.any(aa!=jj,axis=2);Image.fromarray(diff.astype(np.uint8)*255).save(P/'changed-mask.png');assert np.array_equal(aa[m==0],jj[m==0]);assert not diff[:,650:].any()
qa=[]
Q=P/'qa';Q.mkdir(exist_ok=True)
for name,box in [('upper-return',(180,0,560,345)),('west-return',(120,270,500,710)),('x3981-upper',(235,0,335,760)),('x3981-lower',(235,650,335,1254)),('x0-protected',(360,0,460,1254))]:
 p=Q/(name+'.png');joined.crop(box).save(p);qa.append({'file':str(p),'sha256':sha(p),'cropLTRB':box,'nativeScale':1,'actuallyViewed':False})
ys,xs=np.where(diff)
rec={'file':str(P/'joined.png'),'sha256':sha(P/'joined.png'),'pixels':[1254,1254],'tileLocalWindowLTRB':req['tileLocalWindowLTRB'],'context':{'file':str(P/'context.png'),'sha256':sha(P/'context.png'),'boundSourceParts':req['sourceParts']},'operation':'Coordinate-identical local AI surface seam repair, alpha composite within two small polygons/rectangles; no resampling or registration.','derivedFrom':[{'file':str(P/'context.png'),'sha256':sha(P/'context.png'),'generationRecord':str(P/'context.png.generation.json')},{'file':str(P/'native.png'),'sha256':sha(P/'native.png'),'generationRecord':str(P/'native.png.generation.json')}],'alphaMask':{'file':str(P/'alpha-mask.png'),'sha256':sha(P/'alpha-mask.png')},'changedMask':{'file':str(P/'changed-mask.png'),'sha256':sha(P/'changed-mask.png')},'regions':[{'name':n,'localLTRB':box,'transition':f} for n,box,f in regions],'proof':{'outsideMaskExact':True,'C10AtAndBeyond250Exact':True,'changedPixels':int(diff.sum()),'changedBoundingC10LTRB':[int(xs.min())-400,int(ys.min())+850,int(xs.max())-399,int(ys.max())+851],'nativeScale':1,'resampling':False},'qa':qa,'formalAccepted':False,'status':'pending_actual_visual_review'}
(P/'manifest.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');(P/'joined.png.generation.json').write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8');print(json.dumps({'file':rec['file'],'sha256':rec['sha256'],'proof':rec['proof']}))

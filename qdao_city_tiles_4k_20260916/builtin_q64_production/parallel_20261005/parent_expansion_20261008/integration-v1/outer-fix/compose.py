from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;E=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
entries=[]
for name,box,feathers in [('north',(150,305,890,530),(32,32,32,32)),('south',(375,340,900,650),(28,40,10,40))]:
 D=P/name;req=json.loads((D/'request.json').read_text(encoding='utf-8-sig'))
 a=Image.open(D/'context.png').convert('RGB');b=Image.open(D/'native.png').convert('RGB');assert a.size==b.size==(1254,1254)
 l,t,r,d=box;fl,ft,fr,fb=feathers;y,x=np.mgrid[t:d,l:r];z=np.clip(np.minimum.reduce([(x-l)/fl,(r-1-x)/fr,(y-t)/ft,(d-1-y)/fb]),0,1);z=z*z*(3-2*z)
 m=np.zeros((1254,1254),np.uint8);m[t:d,l:r]=np.round(z*255).astype(np.uint8);mask=Image.fromarray(m);mask.save(D/'mask.png')
 joined=Image.composite(b,a,mask);joined.save(D/'joined.png')
 aa=np.array(a);jj=np.array(joined);assert np.array_equal(aa[m==0],jj[m==0]);assert np.array_equal(aa[:,900:],jj[:,900:])
 q=D/'qa';q.mkdir(exist_ok=True)
 crop=(max(0,l-80),max(0,t-80),min(1254,r+80),min(1254,d+80));joined.crop(crop).save(q/'full-return.png')
 out={'file':str(D/'joined.png'),'sha256':sha(D/'joined.png'),'pixels':[1254,1254],'operation':'Native coordinate-identical local AI repair with smoothstep alpha mask; no resampling, registration, colour correction or pixel blur.','derivedFrom':[{'file':str(D/'context.png'),'sha256':sha(D/'context.png'),'generationRecord':str(D/'context.png.generation.json')},{'file':str(D/'native.png'),'sha256':sha(D/'native.png'),'generationRecord':str(D/'native.png.generation.json')}],'mask':{'file':str(D/'mask.png'),'sha256':sha(D/'mask.png'),'boundsLocalLTRB':box,'alphaTransitionLTRB':feathers},'source':req['source'],'proof':{'outsideMaskExact':True,'rightAtAndBeyond900Exact':True,'changedPixels':int(np.any(aa!=jj,axis=2).sum()),'resampling':False,'nativePixelScale':1},'qa':[{'file':str(q/'full-return.png'),'sha256':sha(q/'full-return.png'),'cropLTRB':crop,'nativeScale':1,'actuallyViewed':False}],'formalAccepted':False,'status':'pending_visual_review'}
 (D/'joined.png.generation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');(D/'manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');entries.append({'name':name,'file':out['file'],'sha256':out['sha256'],'sourceWindow':req['source']['cropLTRB'],'mask':out['mask'],'manifest':str(D/'manifest.json')})
 westreq=json.loads((P.parent/'outer-qa/manifest.json').read_text(encoding='utf-8-sig'))
 westsource=westreq['westSource'];fix=Path(westreq['c01Source']['file']);assert sha(fix)==westreq['c01Source']['sha256']
 strip=Image.open(fix).convert('RGB').crop((0,0,115,1254));strip.save(P/'west-c09-strip.png')
 old=Image.open(westsource['file']).convert('RGB').crop((3981,909,4096,2163));diff=np.any(np.array(old)!=np.array(strip),axis=2);Image.fromarray(diff.astype(np.uint8)*255).save(P/'west-c09-changed-mask.png')
 wrec={'file':str(P/'west-c09-strip.png'),'sha256':sha(P/'west-c09-strip.png'),'operation':'Exact native left115 crop from repaired c01 for paired c09 update; no resize.','derivedFrom':[{'file':str(fix),'sha256':sha(fix),'generationRecord':str(fix)+'.generation.json','cropLTRB':[0,0,115,1254]}],'targetTile':'r08_c09','targetLTRB':[3981,909,4096,2163],'boundTargetSource':westsource,'changedMask':{'file':str(P/'west-c09-changed-mask.png'),'sha256':sha(P/'west-c09-changed-mask.png')},'changedPixels':int(diff.sum()),'oldRegionPixelSha256':hashlib.sha256(np.array(old).tobytes()).hexdigest(),'actualVisualQA':str(P.parent/'outer-qa/manifest.json'),'writtenBackToChild':False,'formalAccepted':False}
 (P/'west-c09-strip.png.generation.json').write_text(json.dumps(wrec,indent=2)+'\n',encoding='utf-8')
 (P/'manifest.json').write_text(json.dumps({'createdAt':datetime.now(timezone.utc).isoformat(),'repairs':entries,'westPairedUpdate':wrec,'formalAccepted':False,'status':'pending_visual_review'},indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'repairs':entries,'westChangedPixels':wrec['changedPixels']}))

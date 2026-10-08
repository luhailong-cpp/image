from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
req=json.loads((R/'request.json').read_text(encoding='utf-8-sig'))
a=np.array(Image.open(R/'context.png').convert('RGB'));b=np.array(Image.open(R/'native.png').convert('RGB'))
assert a.shape==b.shape==(1254,1254,3)
y,x=np.mgrid[:1254,:1254]
# Local seam support; no image warp, resizing or blur. Smooth alpha only.
w=np.clip((x-400)/150,0,1)*np.clip((850-x)/150,0,1)*np.clip((1050-y)/160,0,1)
w=w*w*(3-2*w)
mask=np.rint(w*255).astype('uint8');Image.fromarray(mask).save(R/'mask.png')
joined=Image.composite(Image.fromarray(b),Image.fromarray(a),Image.fromarray(mask));joined.save(R/'joined.png')
# Second native generation replaces only the short highlight notch and its returns.
tw=np.clip((x-512)/65,0,1)*np.clip((752-x)/65,0,1)*np.clip((y-151)/55,0,1)*np.clip((371-y)/55,0,1)
tw=tw*tw*(3-2*tw);tm=np.rint(tw*255).astype('uint8');Image.fromarray(tm).save(R/'trim-mask.png')
joined=Image.composite(Image.open(R/'trim-gap/native.png').convert('RGB'),joined,Image.fromarray(tm));joined.save(R/'final-joined.png')
out=R/'final-output';out.mkdir(exist_ok=True);j=np.array(joined);outputs=[]
for part in req['parts']:
 p=Path(part['file']);assert sha(p)==part['sha256'];im=Image.open(p).convert('RGB');crop=part['cropLTRB'];dx,dy=part['pasteXY'][:2];width=crop[2]-crop[0];height=crop[3]-crop[1]
 im.paste(joined.crop((dx,dy,dx+width,dy+height)),crop[:2]);dest=out/p.name;im.save(dest)
 before=np.array(Image.open(p).convert('RGB'));after=np.array(im);changed=np.any(before!=after,axis=2)
 record={'file':str(dest),'sha256':sha(dest),'operation':'Two sequential native-scale localized alpha composites only; no image blur/warp/upscale','source':part,'native':{'file':str(R/'native.png'),'sha256':sha(R/'native.png'),'generationRecord':str(R/'native.png.generation.json')},'mask':{'file':str(R/'mask.png'),'sha256':sha(R/'mask.png')},'trimNative':{'file':str(R/'trim-gap/native.png'),'sha256':sha(R/'trim-gap/native.png'),'generationRecord':str(R/'trim-gap/native.png.generation.json')},'trimMask':{'file':str(R/'trim-mask.png'),'sha256':sha(R/'trim-mask.png')},'changedPixels':int(changed.sum()),'formalAccepted':False,'actualModel':None,'actualQuality':None}
 Path(str(dest)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');outputs.append(record)
qa=R/'final-qa';qa.mkdir(exist_ok=True);rows=[]
for name,box in [('upper-relief',[440,0,850,210]),('diagonal-trim',[440,170,850,430]),('gray-upper',[420,340,860,600]),('gray-lower',[420,550,860,850]),('bottom-trim',[420,770,860,1060]),('left-return',[370,240,500,950]),('right-return',[750,240,900,950]),('bottom-return',[400,920,850,1110])]:
 p=qa/f'{name}.png';joined.crop(box).save(p);rows.append({'file':str(p),'sha256':sha(p),'cropLTRB':box,'nativeScale':1,'actuallyViewed':False})
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'assembled_awaiting_visual_review','sourceRequest':str(R/'request.json'),'outputs':outputs,'joined':{'file':str(R/'final-joined.png'),'sha256':sha(R/'final-joined.png')},'qa':rows,'formalAccepted':False,'wholeCityComplete':False,'newCompleteCoordinates':0,'childFilesModified':False}
(R/'final-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'outputs':[e['file'] for e in outputs],'qaCount':len(rows)}))

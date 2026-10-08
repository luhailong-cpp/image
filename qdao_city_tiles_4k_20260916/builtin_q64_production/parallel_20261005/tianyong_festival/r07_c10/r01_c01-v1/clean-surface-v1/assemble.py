from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
req=json.loads((D/'request.json').read_text(encoding='utf-8'))
src=np.array(Image.open(req['source']['file']).convert('RGB'))
new=np.array(Image.open(D/'native.png').convert('RGB'))
h,w=src.shape[:2];yy,xx=np.mgrid[:h,:w]
alpha=np.minimum.reduce([np.clip((xx-510)/20,0,1),np.clip((865-xx)/20,0,1),np.clip((yy-350)/20,0,1),np.clip((680-yy)/20,0,1)])
# Keep the actual source slab's white highlight, bevel, brown joint and all lower
# slab pixels EXACTLY. Only the plain face is replaced with actual AI painting.
# Locate the established highlight in a narrow strip about its known straight path.
edge=np.full(w,1254,dtype=np.int32)
for x in range(510,866):
 predicted=int(round(0.35*x+442))
 lo,hi=predicted-10,predicted+11
 edge[x]=lo+int(np.argmax(src[lo:hi,x].mean(1)))
guard=(yy>=edge[None,:]-3)&(xx>=510)&(xx<=865)
alpha*=np.clip((edge[None,:]-3-yy)/6,0,1)
out=np.rint(src*(1-alpha[:,:,None])+new*alpha[:,:,None]).clip(0,255).astype(np.uint8)
assert np.array_equal(src[guard],out[guard])
assert np.array_equal(src[alpha==0],out[alpha==0])
Image.fromarray(out).save(D/'joined.png')
Image.fromarray(np.uint8(alpha*255)).save(D/'repair-mask.png')
Image.fromarray(np.uint8(guard)*255).save(D/'preserved-edge-mask.png')
Image.fromarray(out).crop((480,320,900,710)).save(D/'defect-after.png')
Image.fromarray(out).crop((470,570,910,780)).save(D/'edge-return-qa.png')
Image.fromarray(out).crop((470,300,550,710)).save(D/'left-return-qa.png')
Image.fromarray(out).crop((825,300,910,740)).save(D/'right-return-qa.png')
diff=np.any(out!=src,axis=2);yy2,xx2=np.where(diff)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':[req['source'],info(D/'native.png')],'joined':info(D/'joined.png'),'method':'Native AI repaint of flat slab face; exact-source recovery outside explicit texture-only mask and across original lower white highlight, bevel and stone joint. No blur, resize, warp, sharpening or tone adjustment.','nativeScale':1,'maxAbsDx':0,'maxAbsDy':0,'maxAbsToneRGB':0,'mask':info(D/'repair-mask.png'),'preservedEdgeMask':info(D/'preserved-edge-mask.png'),'sourceExactOutsideMask':True,'sourceExactAtAndBelowSlabHighlight':True,'changedNativeBoundsLTRB':[int(xx2.min()),int(yy2.min()),int(xx2.max()+1),int(yy2.max()+1)],'changedPixels':int(diff.sum()),'excludedFinding':req['excludedFinding']}
(D/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record))

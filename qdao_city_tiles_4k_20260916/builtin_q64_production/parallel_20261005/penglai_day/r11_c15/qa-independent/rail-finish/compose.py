from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
O=Path(__file__).resolve().parent
a=np.array(Image.open(O/'input.png'),np.float32);b=np.array(Image.open(O/'generated-v1.png'),np.float32)
Y,X=np.indices(a.shape[:2]);alpha=np.zeros(a.shape[:2],np.float32)
spec=[]
for name,cx,cy in [('upper',640,378),('lower',632,1003)]:
 pred=.59*(np.arange(1254)-cx)+cy
 centers=[]
 for im in [a,b]:
  c=[]
  for x in range(1254):
   lo=max(0,int(pred[x]-10));hi=min(1254,int(pred[x]+10))
   ys=np.arange(lo,hi)
   if len(ys)==0:c.append(pred[x]);continue
   w=np.maximum(im[lo:hi,x,2]-180,0)**4
   c.append((ys*w).sum()/w.sum() if w.sum()>0 else pred[x])
  centers.append(np.array(c))
 ca,cb=centers
 def cost(x):
  ys=np.arange(max(0,int(pred[x]-15)),min(1254,int(pred[x]+15)))
  return float(np.mean(np.minimum(abs(a[ys,x]-b[ys,x]),40)**2)+100*abs(ca[x]-cb[x])**2)
 left=min(range(cx-115,cx-55),key=cost);right=min(range(cx+55,cx+115),key=cost)
 # Narrow band around the existing highlight; pixel data are unresampled native AI.
 loLine=np.minimum(ca,cb)-16;hiLine=np.maximum(ca,cb)+16
 dx=np.minimum(X-left,right-X);dy=np.minimum(Y-loLine[None,:],hiLine[None,:]-Y)
 endTransition=24 if name=="upper" else 48
 m=np.minimum(np.clip(dx/endTransition,0,1),np.clip(dy/6,0,1))
 alpha=np.maximum(alpha,m)
 spec.append({'name':name,'left':left,'right':right,'halfWidth':16,'endTransition':endTransition,'sideTransition':6,'centerTarget':[cx,cy],'leftCost':cost(left),'rightCost':cost(right),'centerMismatchAtEnds':[float(ca[left]-cb[left]),float(ca[right]-cb[right])]})
alpha=np.rint(alpha*255).astype('uint8')
rep=np.array(Image.open(O/'generated-v1.png'));weight=alpha.astype('float32')/255
out=np.rint(rep*weight[:,:,None]+a*(1-weight[:,:,None])).astype('uint8')
assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p,refs,op):
 size=Image.open(p).size;Image.open(p).verify()
 d={'file':str(p),'sha256':sha(p),'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'width':size[0],'height':size[1],'format':'PNG','derivedFrom':[{'file':str(s),'sha256':sha(s),'generationRecord':str(s)+'.generation.json'} for s in refs],'operation':op,'formalAccepted':False}
 Path(str(p)+'.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
rp=O/'replacement.png';mp=O/'alpha.png';cp=O/'composite.png'
Image.fromarray(rep).save(rp);record(rp,[O/'generated-v1.png'],{'method':'native AI pixels unchanged','resampling':False,'imageBlur':False,'colorField':None})
Image.fromarray(alpha).save(mp);record(mp,[O/'input.png',O/'generated-v1.png'],{'method':'two very local rail highlight bands; only mask coverage transitions','spec':spec,'imageBlur':False,'warp':False,'resampling':False})
Image.fromarray(out).save(cp);record(cp,[O/'input.png',rp,mp],{'method':'round(alpha/255 * replacement + (1-alpha/255) * base); composite once','outsideMaskIdentical':True,'imageBlur':False,'warp':False,'resampling':False})
yy,xx=np.where(alpha>0);changed=np.any(out!=a.astype('uint8'),axis=2);yc,xc=np.where(changed)
manifest={'base':str(O.parent.parent/'repairs/internal/r11_c15-internal-candidate-v5.png'),'baseSHA256':'06f948bfa9e503a624f2469d7d80d63785aafa9c33fb83df43a677b1970f0538','origin':[1600,2200],'replacement':str(rp),'replacementSHA256':sha(rp),'mask':str(mp),'maskSHA256':sha(mp),'maskType':'8-bit alpha; composite once','composite':str(cp),'compositeSHA256':sha(cp),'supportBBoxLocal':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'supportBBoxTile':[int(xx.min()+1600),int(yy.min()+2200),int(xx.max()+1601),int(yy.max()+2201)],'changedPixels':int(changed.sum()),'outsideMaskIdentical':True,'spec':spec,'qa':'pending full native composite and local return inspection','formalAccepted':False}
(O/'merge-manifest-v1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
for name,box in [('upper-composite',[475,255,825,495]),('lower-composite',[470,865,820,1125])]:
 p=O/(name+'.png');Image.fromarray(out).crop(box).save(p)
 record(p,[cp],{'method':'native integer QA crop','bbox':box})
print(json.dumps(manifest,indent=2))


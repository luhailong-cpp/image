from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parent.parent;sys.path.insert(0,str(O));import ai_helper as h;sys.path.insert(0,str(R/'repairs/internal'));import quilt as q
st=json.loads((O/'state-after-east-v1.json').read_text(encoding='utf8'));ims={k:Image.open(v).convert('RGB') for k,v in st['current'].items()};Y,X=np.indices((1254,1254));mani=[]
def matte(m,w):
 z=m.copy();d=m.astype('float32')
 for _ in range(w-1):z &= np.roll(z,1,0)&np.roll(z,-1,0)&np.roll(z,1,1)&np.roll(z,-1,1);d+=z
 return np.rint(np.minimum(d/w,1)*255).astype('uint8')
def line_mask(points,width):
 p=Image.new('L',(1254,1254));ImageDraw.Draw(p).line(points,fill=255,width=width,joint='curve');return np.asarray(p)>0
for n in ['north-return','ne-return','rail-return']:
 src=O/(n+'-source.png');gen=O/(n+'-generated.png');a=np.asarray(Image.open(src),np.float32);b=np.asarray(Image.open(gen),np.float32)
 exception=np.zeros((1254,1254),bool)
 if n=='north-return':m=(X>=557)&(X<815)&(Y>=460)&(Y<920);alpha=matte(m,20)
 elif n=='ne-return':
  # One narrowly approved exception only around former false plank stubs.
  upper=line_mask([(370,634),(588,485)],54);lower=line_mask([(445,688),(590,594)],54);stub=line_mask([(510,702),(588,652)],52)
  main=(upper|lower|stub)&(X<589)&(X>=300)&(Y>=450)&(Y<740)
  notch=line_mask([(396,283),(539,188)],45)&(X<539)
  edge=(X>1000)&(X<1220)&(Y>=757)&(Y<890)
  m=main|notch|edge;alpha=matte(m,10);exception=(X>=539)&(Y<757)&(alpha>0);assert not np.any(exception&(X>=589))
 else:
  m=line_mask([(532,1082),(743,1247)],46)&(Y<1254);alpha=matte(m,10)
 al=alpha[:,:,None].astype('float32')/255;grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=(alpha>0)&(alpha<255)&(grad<40)&(np.max(abs(a-b),axis=2)<80);w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-24,24)*np.clip(w*30,0,1);rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.rint(rep*al+a*(1-al)).astype('uint8');assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0]);changed=np.any(out!=a,axis=2);ex=exception&changed
 rec={'method':'already returned nativeAI exact alpha composite once; boundedRGB24 perimeter; no blur or resampling','scopeChange':'No new generation after parent stop; reuse-material mechanical finish','protectedCoreException':{'authorization':'root permitted only this existing <=50px narrow plank-contour return exception','pixelCount':int(ex.sum()),'maxDepth':int(X[ex].max()-538) if ex.any() else 0,'bboxLocal':list(Image.fromarray((ex*255).astype('uint8')).getbbox()) if ex.any() else None}}
 outpaths={}
 for label,arr in [('alpha',alpha),('replacement',rep),('composite',out),('actual-diff-mask',(changed*255).astype('uint8')),('core-exception-mask',(ex*255).astype('uint8'))]:
  p=O/(n+'-v2-'+label+'.png');Image.fromarray(arr).save(p);q.record(p,[src,gen],rec);outpaths[label]=str(p)
 fp=O/(n+'-v2-field.npz');np.savez_compressed(fp,field=f);mani.append({'name':n,**outpaths,**rec,'field':str(fp),'fieldSha256':q.sha(fp)})
 outim=Image.fromarray(out)
 if n=='north-return':ims['r10_c14'].paste(outim.crop((0,0,1254,627)),(0,3469));ims['r11_c14'].paste(outim.crop((0,627,1254,1254)),(0,0))
 elif n=='ne-return':
  ims['r10_c14'].paste(outim.crop((0,0,1096,200)),(3000,3896));ims['r10_c15'].paste(outim.crop((1096,0,1254,200)),(0,3896));ims['r11_c14'].paste(outim.crop((0,200,1096,1254)),(3000,0));ims['r11_c15'].paste(outim.crop((1096,200,1254,1254)),(0,0))
 else:ims['r11_c14'].paste(outim,(2450,2842))
for k,im in ims.items():
 p=O/(k+'-reuse-candidate-v2.png');im.save(p);q.record(p,[Path(st['current'][k])]+[Path(v['composite']) for v in mani],{'method':'already composited exact return crops pasted; no repeated alpha or resampling','scope':'archived-scope reuse material; not formally accepted'});st['current'][k]=str(p)
st['returnRepairs']=mani;st['scope']='old16x16 stopped; reusable candidates only; parent changed to6x6';(O/'state-reuse-v2.json').write_text(json.dumps(st,indent=2),encoding='utf8');print([(v['name'],v['protectedCoreException']) for v in mani])


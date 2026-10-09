from pathlib import Path
import sys,json,numpy as np
from PIL import Image
def distance_transform_edt(m):
 d=m.astype('float32');z=m.copy()
 for _ in range(15):
  z &= np.roll(z,1,0)&np.roll(z,-1,0)&np.roll(z,1,1)&np.roll(z,-1,1)
  d+=z
 return d
O=Path(__file__).resolve().parent;R=O.parent.parent
sys.path.insert(0,str(O));import ai_helper as h;import quilt as q
G=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,g in [('boom-return','33740139-70c0-419f-9a44-bc11d2d3469e'),('post-return','9b64877d-d506-48ad-a81f-98049d4fcd0a'),('hull-return','5761501f-03e1-4384-ac9a-c32ac04bffd1')]:h.ingest(n,G/('exec-'+g+'.png'))
def cut(cost,lo,hi):
 c=cost[:,lo:hi];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.2,dp,np.r_[dp[1:],1e12]+.2]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+z[k,np.arange(w)]
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+lo
src=O/'r11_c15-internal-candidate-v4.png';canvas=Image.open(src).convert('RGB');manifest=[]
for n,xy,_ in json.loads((O/'finish-spec.json').read_text(encoding='utf8')):
 x,y=xy;gen=O/(n+'-generated.png');a=np.asarray(canvas.crop((x,y,x+1254,y+1254)),np.float32);b=np.asarray(Image.open(gen),np.float32);cost=np.mean(np.minimum(abs(a-b),70)**2,axis=2);Y,X=np.indices((1254,1254));m=np.zeros((1254,1254),bool);paths={}
 boxes={'boom-return':[[[300,410],[785,855],[445,500],[680,740]]],'post-return':[[[480,545],[720,780],[465,515],[730,790]]],'hull-return':[[[200,260],[460,530],[30,75],[1100,1200]],[[600,665],[1000,1080],[30,75],[1100,1200]]]}
 for i,rr in enumerate(boxes[n]):
  l=cut(cost,*rr[0]);r=cut(cost,*rr[1]);t=cut(cost.T,*rr[2]);d=cut(cost.T,*rr[3]);m|=(X>=l[:,None])&(X<r[:,None])&(Y>=t[None,:])&(Y<d[None,:]);paths.update({f'l{i}':l,f'r{i}':r,f't{i}':t,f'd{i}':d})
 alpha=np.minimum(distance_transform_edt(m)/16,1).astype('float32');alpha=np.rint(alpha*255)/255
 border=(alpha>0)&(alpha<1);grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=border&(grad<35)&(np.max(abs(a-b),axis=2)<70)
 w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-24,24)*np.clip(w*60,0,1)
 rep=np.clip(np.rint(b+f),0,255).astype('uint8');mp=O/(n+'-v5-alpha.png');rp=O/(n+'-v5-replacement.png');cp=O/(n+'-v5-composite.png');fp=O/(n+'-v5-fields.npz');np.savez_compressed(fp,field=f,**paths)
 Image.fromarray((alpha*255).astype('uint8')).save(mp);Image.fromarray(rep).save(rp);out=np.rint(rep*alpha[:,:,None]+a*(1-alpha[:,:,None])).astype('uint8');Image.fromarray(out).save(cp);refs=[src,gen]
 q.record(mp,refs,{'method':'exact alpha matte over native AI correction with adaptive ownership boundary','matteTransitionPixels':16,'imageBlur':False,'sourceResampling':False,'ranges':boxes[n],'origin':xy})
 q.record(rp,refs+[mp],{'method':'native AI with bounded additive RGB perimeter match','cap':24,'fields':str(fp),'fieldSha256':q.sha(fp),'actualMax':float(abs(f).max()),'imageBlur':False,'sourceResampling':False})
 q.record(cp,refs+[mp,rp],{'method':'exact alpha composite','outsideSupportIdentical':True});assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0]);canvas.paste(Image.fromarray(out),(x,y));manifest.append({'name':n,'origin':xy,'replacement':str(rp),'replacementSha256':q.sha(rp),'mask':str(mp),'maskSha256':q.sha(mp),'maskType':'alpha exact; composite once'})
dst=O/'r11_c15-internal-candidate-v5.png';canvas.save(dst);q.record(dst,[src]+[Path(z[k]) for z in manifest for k in ['replacement','mask']],{'method':'three native AI microcontinuity repairs; 16px matte transition only; no image blur or resampling'});q.qa(np.asarray(canvas),'v5',dst);p=R/'preview-internal-v5.png';canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(p);q.record(p,[dst],{'method':'preview only downscale'});(O/'ai-merge-manifest-v5.json').write_text(json.dumps({'base':str(src),'candidate':str(dst),'sha256':q.sha(dst),'repairs':manifest},indent=2),encoding='utf8');print(q.sha(dst))

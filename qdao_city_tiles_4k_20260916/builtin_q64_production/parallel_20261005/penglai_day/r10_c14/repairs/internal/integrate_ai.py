import quilt as q
import numpy as np,json
from PIL import Image
def cut(cost,a,b):
 c=cost[:,a:b];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.3,dp,np.r_[dp[1:],1e12]+.3]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+np.min(z,axis=0)
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+a
specs={
 'stonecap':{'origin':[1500,397],'left':[320,380],'right':[810,875],'top':[350,415],'bottom':[1130,1200]},
 'wallmiddle':{'origin':[1000,1421],'left':[320,400],'right':[925,995],'top':[270,350],'bottom':[935,1015]},
 'wallright':{'origin':[1940,1421],'left':[175,255],'right':[995,1065],'top':[450,520],'bottom':[810,905]},
 'tilebevel':{'origin':[397,750],'left':[390,470],'right':[765,845],'top':[375,450],'bottom':[685,750]}
}
src=q.O/'r10_c14-internal-candidate-v2.png';canvas=Image.open(src).convert('RGB');manifest=[];total=Image.new('L',(4096,4096))
for n,s in specs.items():
 inp=q.O/(n+'-edit-input.png');gen=q.O/(n+'-ai-v1-generated.png');a=np.asarray(Image.open(inp).convert('RGB'),np.float32);b=np.asarray(Image.open(gen).convert('RGB'),np.float32);cost=np.mean(np.minimum(abs(a-b),50)**2,axis=2)
 left=cut(cost,*s['left']);right=cut(cost,*s['right']);top=cut(cost.T,*s['top']);bottom=cut(cost.T,*s['bottom']) if s['bottom'] else np.full(1254,1254)
 Y,X=np.indices((1254,1254));m=(X>=left[:,None])&(X<right[:,None])&(Y>=top[None,:])&(Y<bottom[None,:])
 border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);reliable=border&(grad<35)&(np.max(abs(a-b),axis=2)<35)
 weight=q.smooth(q.smooth(reliable[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*reliable[:,:,None]));f=np.clip(num/np.maximum(weight,1e-6),-12,12)*np.clip(weight*240,0,1)*m[:,:,None]
 rep=np.clip(np.rint(b+f),0,255).astype('uint8');rp=q.O/(n+'-replacement.png');mp=q.O/(n+'-mask.png');fp=q.O/(n+'-fields.npz');np.savez_compressed(fp,fields=f,left=left,right=right,top=top,bottom=bottom);Image.fromarray(rep).save(rp);Image.fromarray((m*255).astype('uint8')).save(mp)
 q.record(mp,[inp,gen],{'method':'minimum-error binary ownership within stated boundary ranges','ranges':s,'feather':False});q.record(rp,[gen,inp,mp],{'method':'bounded additiveRGB correction at reliable perimeter only','maxCorrection':float(abs(f).max()),'cap':12,'fieldFile':str(fp),'fieldSha256':q.sha(fp),'imageBlur':False,'imageResampling':False,'fieldSmoothing':'two49pxbox filters, fields only'})
 cp=q.O/(n+'-composite.png');Image.composite(Image.fromarray(rep),Image.fromarray(a.astype('uint8')),Image.fromarray((m*255).astype('uint8'))).save(cp);q.record(cp,[inp,rp,mp],{'method':'integer binary ownership composite; pixels outside mask identical'})
 canvas.paste(Image.fromarray(rep),tuple(s['origin']),Image.fromarray((m*255).astype('uint8')));total.paste(255,tuple(s['origin']),Image.fromarray((m*255).astype('uint8')));manifest.append(dict(name=n,origin=s['origin'],replacement=str(rp),mask=str(mp),replacementSha256=q.sha(rp),maskSha256=q.sha(mp)))
dest=q.O/'r10_c14-internal-candidate-v3.png';canvas.save(dest);q.record(dest,[src]+[q.O/(n+e) for n in specs for e in ['-replacement.png','-mask.png']],{'method':'AI repair of stonecap, stone wall grooves and paving bevel joins, binary local masks, no image resize/blur; inherits bounded source translations from v2','formalAccepted':False});q.qa(np.asarray(canvas),'v3',dest)
tp=q.O/'internal-v3-change-mask.png';total.save(tp);q.record(tp,[src,dest],{'method':'union of binary AI repair masks, no feather; pixels outside mask unchanged'})
assert np.array_equal(np.asarray(canvas)[:627],np.asarray(Image.open(src))[:627])
assert np.array_equal(np.asarray(canvas)[:,:627],np.asarray(Image.open(src))[:,:627])
assert np.array_equal(np.asarray(canvas)[-627:],np.asarray(Image.open(src))[-627:])
(q.O/'ai-merge-manifest.json').write_text(json.dumps({'base':str(src),'candidate':str(dest),'sha256':q.sha(dest),'repairs':manifest,'changeMask':str(tp),'changeMaskSha256':q.sha(tp),'unchangedBands':['north627','west627','south627'],'formalAccepted':False},indent=2),encoding='utf8')
print(str(dest),q.sha(dest))

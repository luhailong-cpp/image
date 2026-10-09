from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O));import quilt as q
R=O.parent.parent
src=R/'tiles/r10_c15-candidate-review-v1.png';gen=O/'left-pile-generated.png'
a=np.asarray(Image.open(src).convert('RGB'),np.float32)[397:1651,:1254];b=np.asarray(Image.open(gen).convert('RGB'),np.float32)
Y,X=np.indices((1254,1254))
im=Image.new('L',(1254,1254));d=ImageDraw.Draw(im)
d.polygon([(395,245),(447,245),(447,1120),(392,1120)],fill=255)
d.line([(278,635),(420,551)],fill=255,width=34)
m=np.asarray(im)>0
# Match static native ownership endpoints in nearby low-error rows.
cost=np.mean(np.minimum(abs(a-b),50)**2,axis=2)
def cut(c,lo,hi):
 c=c[:,lo:hi];h,w=c.shape;dp=c[0].copy();back=np.zeros((h,w),np.int16)
 for y in range(1,h):
  z=np.stack([np.r_[1e12,dp[:-1]]+.3,dp,np.r_[dp[1:],1e12]+.3]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+z[k,np.arange(w)]
 p=np.zeros(h,np.int32);p[-1]=np.argmin(dp)
 for y in range(h-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+lo
top=cut(cost.T,230,330);bottom=cut(cost.T,1080,1160)
m=(m|((X>=395)&(X<=447)&(Y>230)&(Y<1160)))&(Y>=top[None,:])&(Y<bottom[None,:])
border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1))
grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2)
rel=border&(grad<35)&(np.max(abs(a-b),axis=2)<80)
w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]))
f=np.clip(num/np.maximum(w,1e-6),-32,32)*np.clip(w*240,0,1)*m[:,:,None]
rep=np.clip(np.rint(b+f),0,255).astype('uint8')
rp=O/'pile-outline-v5-replacement.png';mp=O/'pile-outline-v5-mask.png';fp=O/'pile-outline-v5-fields.npz'
Image.fromarray(rep).save(rp);Image.fromarray(m.astype('uint8')*255).save(mp);np.savez_compressed(fp,field=f,top=top,bottom=bottom)
q.record(mp,[src,gen],{'method':'narrow binary corridor along existing pile edge and brace underside; minimum-error endpoint ownership','cropOrigin':[0,397],'noFeather':True})
q.record(rp,[src,gen,mp],{'method':'genuine native AI with bounded additive RGB perimeter correction','cap':32,'maxField':float(abs(f).max()),'fieldFile':str(fp),'fieldSha256':q.sha(fp),'imageBlur':False,'imageResampling':False})
out=Image.open(src).convert('RGB');out.paste(Image.fromarray(rep),(0,397),Image.fromarray(m.astype('uint8')*255))
dest=R/'tiles/r10_c15-candidate-review-v2.png';out.save(dest);q.record(dest,[src,rp,mp],{'method':'precise AI contour repair; pixels outside local mask unchanged','origin':[0,397]})
cp=R/'qa/pile-edge-v5.png';out.crop((270,580,650,1570)).save(cp);q.record(cp,[dest],{'method':'native crop','boxLTRB':[270,580,650,1570]})
print(q.sha(dest))

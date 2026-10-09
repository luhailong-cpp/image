from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parent.parent
sys.path.insert(0,str(O));import quilt as q;import ai_helper as h
for f in ['pile-lip.call.json','pile-lip.roles.json','pile-lip.prompt.txt']:
 p=O/f;p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf8')
gen=h.ingest('pile-lip',r'C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c/exec-6740233a-487d-4755-9097-4ddb369fd33f.png')
src=R/'tiles/r10_c15-candidate-review-v1.png';a=np.asarray(Image.open(O/'pile-lip-source.png'),np.float32);b=np.asarray(Image.open(gen),np.float32)
im=Image.new('L',(1254,1254));d=ImageDraw.Draw(im);d.polygon([(395,495),(450,495),(450,600),(397,600)],fill=255);d.polygon([(310,603),(395,550),(422,575),(328,634)],fill=255);m=np.asarray(im)>0
def cut(c,lo,hi):
 c=c[:,lo:hi];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.05,dp,np.r_[dp[1:],1e12]+.05]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+z[k,np.arange(w)]
 path=np.zeros(n,np.int32);path[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):path[y-1]=path[y]+back[y,path[y]]
 return path+lo
cost=np.mean((a-b)**2,axis=2);top=cut(cost.T,420,448);bottom=cut(cost.T,1090,1120)
Y,X=np.indices((1254,1254));m=((X>=395)&(X<450)&(Y>=top[None,:])&(Y<bottom[None,:]))|((np.asarray(im)>0)&(X<397))

border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=border&(grad<35)&(np.max(abs(a-b),axis=2)<80)
w=q.smooth(q.smooth(rel[:,:,None].astype('float32'),12),12);num=q.smooth(q.smooth((a-b)*rel[:,:,None],12),12);f=np.clip(num/np.maximum(w,1e-6),-24,24)*np.clip(w*120,0,1)*m[:,:,None]
rep=np.clip(np.rint(b+f),0,255).astype('uint8');mp=O/'pile-lip-final-mask.png';rp=O/'pile-lip-final-replacement.png';fp=O/'pile-lip-final-fields.npz'
Image.fromarray(m.astype('uint8')*255).save(mp);Image.fromarray(rep).save(rp);np.savez_compressed(fp,field=f)
q.record(mp,[src,gen],{'method':'narrow pile contour between two natural beam intersections plus short brace underside; minimum-error endpoints','origin':[0,397],'noFeather':True})
q.record(rp,[src,gen,mp],{'method':'genuine native AI with bounded additive RGB perimeter field','cap':24,'actualMaxField':float(abs(f).max()),'fieldFile':str(fp),'fieldSha256':q.sha(fp),'imageBlur':False,'imageResampling':False})
out=Image.open(src).convert('RGB');out.paste(Image.fromarray(rep),(0,397),Image.fromarray(m.astype('uint8')*255));dest=R/'tiles/r10_c15-candidate-review-v3.png';out.save(dest);q.record(dest,[src,rp,mp],{'method':'precise native AI contour repair at final QA; outside local binary mask byte-identical','origin':[0,397]})
cp=R/'qa/pile-lip-final.png';out.crop((270,820,650,1120)).save(cp);q.record(cp,[dest],{'method':'native crop','boxLTRB':[270,820,650,1120]})
print(q.sha(dest))

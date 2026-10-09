import sys
sys.dont_write_bytecode=True
import quilt as q
import numpy as np,json
from PIL import Image,ImageDraw
def cut(cost,a,b):
 c=cost[:,a:b];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.3,dp,np.r_[dp[1:],1e12]+.3]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+np.min(z,axis=0)
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+a
specs={
 'deck-narrow':{'origin':[397,0],'left':[460,555],'right':[700,790],'top':None,'bottom':None},
 'left-pile':{'origin':[0,397],'left':None,'right':[650,740],'top':[330,460],'bottom':[800,930]},
 'right-pile':{'origin':[2842,2445],'left':[390,470],'right':[1090,1170],'top':[360,450],'bottom':[820,960]},
 'sail-spar':{'origin':[1421,2842],'left':[400,490],'right':[750,790],'top':None,'bottom':None}
}
src=q.O/'r10_c15-internal-candidate-v1.png';canvas=Image.open(src).convert('RGB');manifest=[]
for n,s in specs.items():
 inp=q.O/(('deck-rail' if n=='deck-narrow' else n)+'-source.png');gen=q.O/(n+'-generated.png');a=np.asarray(Image.open(inp).convert('RGB'),np.float32);b=np.asarray(Image.open(gen).convert('RGB'),np.float32);cost=np.mean(np.minimum(abs(a-b),50)**2,axis=2)
 left=cut(cost,*s['left']) if s['left'] else np.zeros(1254);right=cut(cost,*s['right']) if s['right'] else np.full(1254,1254);top=cut(cost.T,*s['top']) if s['top'] else np.zeros(1254);bottom=cut(cost.T,*s['bottom']) if s['bottom'] else np.full(1254,1254)
 Y,X=np.indices((1254,1254));m=(X>=left[:,None])&(X<right[:,None])&(Y>=top[None,:])&(Y<bottom[None,:])
 if n=='deck-narrow':
  extra=Image.new('L',(1254,1254));ed=ImageDraw.Draw(extra)
  ed.line([(315,372),(1020,-8)],fill=255,width=76)
  ed.line([(457,452),(1260,24)],fill=255,width=66)
  m |= np.asarray(extra)>0
 if n=='left-pile':
  m[:,405:431]=False
  m[(X>=595)&(X<=620)&(Y>565)]=False
 border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));border[[0,-1],:]=False;border[:,[0,-1]]=False;grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);reliable=border&(grad<35)&(np.max(abs(a-b),axis=2)<100)
 weight=q.smooth(q.smooth(reliable[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*reliable[:,:,None]));f=np.clip(num/np.maximum(weight,1e-6),-48,48)*np.clip(weight*240,0,1)*m[:,:,None]
 rep=np.clip(np.rint(b+f),0,255).astype('uint8');rp=q.O/(n+'-v4-replacement.png');mp=q.O/(n+'-v4-mask.png');fp=q.O/(n+'-v4-fields.npz');np.savez_compressed(fp,fields=f,left=left,right=right,top=top,bottom=bottom);Image.fromarray(rep).save(rp);Image.fromarray((m*255).astype('uint8')).save(mp)
 q.record(mp,[inp,gen],{'method':'minimum-error binary ownership within stated boundary ranges','ranges':s,'feather':False});q.record(rp,[gen,inp,mp],{'method':'bounded additiveRGB correction at reliable perimeter only','maxCorrection':float(abs(f).max()),'cap':48,'fieldFile':str(fp),'fieldSha256':q.sha(fp),'imageBlur':False,'imageResampling':False,'fieldSmoothing':'two49pxbox filters, fields only'})
 cp=q.O/(n+'-v4-composite.png');Image.composite(Image.fromarray(rep),Image.fromarray(a.astype('uint8')),Image.fromarray((m*255).astype('uint8'))).save(cp);q.record(cp,[inp,rp,mp],{'method':'integer binary ownership composite; pixels outside mask identical'})
 canvas.paste(Image.fromarray(rep),tuple(s['origin']),Image.fromarray((m*255).astype('uint8')));manifest.append(dict(name=n,origin=s['origin'],replacement=str(rp),mask=str(mp),replacementSha256=q.sha(rp),maskSha256=q.sha(mp)))
dest=q.O/'r10_c15-internal-candidate-v4.png';canvas.save(dest);q.record(dest,[src]+[q.O/(n+e) for n in specs for e in ['-v4-replacement.png','-v4-mask.png']],{'method':'AI repair of deck-rail geometric breaks, two wood-pile tonal/outline seams and sail-spar/reflection seam, binary local masks, no image resize/blur','formalAccepted':False});q.qa(np.asarray(canvas),'v4',dest)
(q.O/'ai-merge-manifest-v4.json').write_text(json.dumps({'base':str(src),'candidate':str(dest),'sha256':q.sha(dest),'repairs':manifest,'formalAccepted':False},indent=2),encoding='utf8')
print(str(dest),q.sha(dest))


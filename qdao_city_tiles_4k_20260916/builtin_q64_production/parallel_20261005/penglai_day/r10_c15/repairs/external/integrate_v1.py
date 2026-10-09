from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parent.parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h;import quilt as q
def cut(cost,a,b):
 c=cost[:,a:b];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.3,dp,np.r_[dp[1:],1e12]+.3]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+np.min(z,axis=0)
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+a
def save(a,p,src,op):
 Image.fromarray(np.clip(np.rint(a),0,255).astype('uint8')).save(p);h.derived(p,src,op)
def join(a,b,label,sources):
 # Both oriented tall strips. Seam across horizontal patch overlap.
 aa=a.transpose(1,0,2);bb=b.transpose(1,0,2);n,w,_=aa.shape
 f=np.clip(q.smooth(aa-bb)/2,-12,12);fade=np.minimum(1,np.minimum(np.arange(w),np.arange(w)[::-1])/48)[None,:,None];fa=-f*fade;fb=f*fade;ac=aa+fa;bc=bb+fb
 cost=np.sqrt(np.mean((ac-bc)**2,axis=2))+.6*np.mean(abs(np.diff(aa,axis=1,prepend=aa[:,:1])-np.diff(bb,axis=1,prepend=bb[:,:1])),axis=2);path=cut(cost,35,w-35);own=np.arange(w)[None,:]<path[:,None];out=np.where(own[:,:,None],ac,bc).transpose(1,0,2)
 fp=O/(label+'-fields.npz');np.savez_compressed(fp,path=path,fieldA=fa,fieldB=fb,ownerA=own);mp=O/(label+'-owner.png');save(own.T*255,mp,sources,{'method':'binary native overlap ownership','fieldFile':str(fp),'fieldSha256':h.sha(fp),'perSourceCap':12,'imageBlur':False,'imageResampling':False});return out,mp
state=json.loads((O/'state-v1.json').read_text(encoding='utf8'))
manifest={}
for axis in ['north','west']:
 native=[O/axis/(f'{axis}-{i}-generated.png') for i in range(1,5)]
 a=np.zeros((4096,1254,3),np.float32);arr=lambda p:np.asarray(Image.open(p).convert('RGB'),np.float32).transpose(1,0,2) if axis=='north' else np.asarray(Image.open(p).convert('RGB'),np.float32)
 a[:1254]=arr(native[0]);prevend=1254;owners=[]
 for s,p in zip([1024,2048,2842],native[1:]):
  b=arr(p);ov=prevend-s;mix,mp=join(a[s:prevend],b[:ov],f'{axis}-v1-quilt-{s}',native);a[s:prevend]=mix;a[prevend:s+1254]=b[ov:];prevend=s+1254;owners.append(mp)
 qp=O/(axis+'-ai-strip-v1.png');save(a.transpose(1,0,2) if axis=='north' else a,qp,native+owners,{'method':'native1254overlap quilt no resize'})
 source=O/(axis+'-joint-source.png');base=arr(source);b=a
 # Exclude a new, unrequested wall joint: preserve original wall geometry with only low-frequency RGB palette correction.
 extra_fields={}
 if axis=='west':
  pm=Image.new('L',(1254,4096));d=ImageDraw.Draw(pm);d.polygon([(525,883),(795,730),(908,807),(570,1029)],fill=255)
  preserve=np.asarray(pm)>0
  diff=b-base;valid=(np.max(abs(diff),axis=2)<45)&(np.max(abs(np.diff(b,axis=1,prepend=b[:,:1])),axis=2)<35)
  w=q.smooth(q.smooth(valid[:,:,None].astype('float32')));num=q.smooth(q.smooth(diff*valid[:,:,None]));col=np.clip(num/np.maximum(w,1e-6),-16,16);b=b.copy();b[preserve]=(base+col)[preserve];extra_fields={'wallGeometryPreserved':preserve,'wallColorDelta':col}
 cost=np.mean(np.minimum(abs(base-b),50)**2,axis=2)
 ranges=([330,465],[990,1120]) if axis=='north' else ([200,315],[900,1020])
 left=cut(cost,*ranges[0]);right=cut(cost,*ranges[1]);Y,X=np.indices((4096,1254));m=(X>=left[:,None])&(X<right[:,None])&(Y>=557)
 border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));border[[0,-1]]=False;border[:,[0,-1]]=False
 grad=np.max(abs(base-np.roll(base,1,0))+abs(base-np.roll(base,1,1)),axis=2);rel=border&(grad<35)&(np.max(abs(base-b),axis=2)<60)
 w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((base-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-24,24)*np.clip(w*240,0,1)*m[:,:,None]
 rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.where(m[:,:,None],rep,base.astype('uint8'))
 restore=lambda z:np.swapaxes(z,0,1) if axis=='north' else z
 fp=O/(axis+'-v1-fields.npz');np.savez_compressed(fp,left=left,right=right,field=f,**extra_fields)
 rp=O/(axis+'-v1-replacement.png');mp=O/(axis+'-v1-mask.png');dest=O/(axis+'-joint-candidate-v1.png')
 save(restore(m*255),mp,[source,qp],{'method':'single continuous binary ownership, first557 along shared edge protected','boundaryRanges':ranges,'noFeather':True})
 save(restore(rep),rp,[source,qp,mp],{'method':'bounded additiveRGB perimeter correction','cap':24,'fieldFile':str(fp),'fieldSha256':h.sha(fp),'imageBlur':False,'imageResampling':False,'wallGeometryPreservation':axis=='west'})
 save(restore(out),dest,[source,rp,mp],{'method':'exact binary composite','outsideMaskIdentical':True})
 assert np.array_equal(out[~m],base.astype('uint8')[~m])
 manifest[axis]={'joint':str(dest),'sha256':h.sha(dest),'mask':str(mp),'maskSha256':h.sha(mp),'replacement':str(rp),'source':str(source),'globalOrigin':state['jointOrigins'][axis],'protectedAlongEdge':557,'sources':[{'file':str(p),'sha256':h.sha(p)} for p in native]}
 img=Image.open(dest)
 for k,s in enumerate([0,1024,2048,2842],1):
  box=(s,0,s+1254,1254) if axis=='north' else (0,s,1254,s+1254);p=O/(f'qa-{axis}-v1-{k}.png');img.crop(box).save(p);h.derived(p,[dest],{'method':'native crop','boxLTRB':box})
(O/'joint-merge-manifest-v1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('joint v1 candidates ready')

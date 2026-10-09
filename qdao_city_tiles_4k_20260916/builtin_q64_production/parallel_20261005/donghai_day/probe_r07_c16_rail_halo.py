import numpy as np
from PIL import Image
import assembly_r07_c16 as a
import integrate_c15_repairs as j
import repair_r07_c16_rail_edge as p
D=p.D/'south-boundary';M=D/'halo-probe-masks';j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
b=j.rgb(p.S);s=j.rgb(p.SO);ex=j.rgb(p.SO.parent/'extended-context.png')
h=ex[:115,115:895];before=b[-115:,:780]
mixed,info=j.joint.join_overlap(before,h,'horizontal',[0,3981,780,4096],'halo-native-probe',j.FN)
alpha=np.asarray(Image.open(info['maskPng']['file']),dtype=np.float32)/255
_,ri=j.joint.join_overlap(h[:,-100:],before[:,-100:],'vertical',[680,3981,780,4096],'halo-native-right',j.FN)
alpha[:,-100:]=np.minimum(alpha[:,-100:],1-np.asarray(Image.open(ri['maskPng']['file']),dtype=np.float32)/255)
mixed=a.blend(before,h,np.rint(alpha*255).astype(np.uint8))
def smooth(v,n=21):
 for _ in range(2):
  for axis in (0,1):
   pads=[(0,0)]*v.ndim;pads[axis]=(n//2,n//2);p=np.pad(v,pads,mode='reflect');c=np.cumsum(p,axis=axis,dtype=np.float64);c=np.concatenate([np.take(c,[0],axis=axis)*0,c],axis=axis)
   v=(c[n:]-c[:-n])/n if axis==0 else (c[:,n:]-c[:,:-n])/n
 return v.astype(np.float32)
old=before.astype(np.float32);new=h.astype(np.float32);raw=mixed.astype(np.float32);delta=old-new
warm=lambda z:np.clip((z[...,0]-z[...,2]+8)/40,0,1)
wo=warm(old);wn=warm(new);wr=warm(raw);field=np.zeros_like(raw)
for k in (0,1):
 valid=((wo>.9)&(wn>.9)) if k else ((wo<.1)&(wn<.1))
 den=smooth(valid.astype(np.float32));f=smooth(delta*valid[:,:,None])/np.maximum(den[:,:,None],.001);field+=f*(wr if k else 1-wr)[:,:,None]
soft=smooth(alpha,35);fix=np.clip(field,-80,80)*(alpha-soft)[:,:,None]
# Keep the physical lower edge on exact halo; color matching below handles blue only.
fix*=np.minimum(1,(114-np.arange(115))/24)[:,None,None]
mid=np.clip(raw+fix,0,255)
edge=s[:3,:780].astype(np.float32).mean(0)-mid[-3:].mean(0)
blue=(1-warm(mid));support=(blue[-3:].mean(0)>.95)&((1-warm(s[:3,:780].astype(np.float32))).mean(0)>.95)
for c in range(3):edge[:,c]=np.interp(np.arange(780),np.flatnonzero(support),edge[support,c])
edge=np.stack([np.convolve(np.pad(edge[:,c],(4,4),mode='edge'),np.ones(9)/9,'valid') for c in range(3)],1)
bluefix=np.clip(edge,-32,32)[None,:,:]*np.linspace(0,1,115)[:,None,None]**2*blue[:,:,None]
fix+=bluefix
b[-115:,:780]=np.clip(np.rint(raw+fix),0,255).astype(np.uint8)
np.savez_compressed(D/'halo-DP-probe-fields.npz',alpha=alpha,field=fix)
a.save_image(D/'halo-DP-boundary-probe.png',Image.fromarray(np.concatenate([b[-300:,:760],s[:200,:760]],0)))
a.save_json(D/'halo-DP-boundary-probe.json',dict(seam=info,visualReview='pending',outputModified=False))

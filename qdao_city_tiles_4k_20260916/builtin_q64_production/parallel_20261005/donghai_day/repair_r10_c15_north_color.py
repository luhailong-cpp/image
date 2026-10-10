"""Bounded same-geometry RGB seam corrections; no source/geometry/image resampling."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'r07_c15/repairs/unified/python-deps'))
import cv2
def gaussian_filter1d(v,sigma,axis=0,mode='nearest'):
 return cv2.GaussianBlur(v.reshape(1,len(v),3),(0,1),sigmaX=sigma,borderType=cv2.BORDER_REPLICATE)[0]
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/north-joint/color-match';Q=D/'qa'
S=T/'repairs/north-integrated-v2/candidate.png';N=R/'r09_c15/output/r09_c15.png'
EXPECTED='56aa9499341914dbf11e50fe2d405e768c5874120ee873dc8a4763ae00db40a7';NS='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(v):return hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def smooth(v):return v*v*(3-2*v)
def img(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(v).save(p);return ref(p)
def guided_1d(values,guide,radius=4,sigma=18):
 out=np.zeros_like(values);den=np.zeros((len(values),1),np.float32)
 for off in range(-radius,radius+1):
  ids=np.clip(np.arange(len(values))+off,0,len(values)-1)
  dist=np.sum((guide-guide[ids])**2,axis=1)
  w=(np.exp(-dist/(2*sigma*sigma))*np.exp(-off*off/(2*(radius/2+1)**2)))[:,None]
  out+=values[ids]*w;den+=w
 return out/np.maximum(den,1e-9)
def main():
 assert sha(S)==EXPECTED and sha(N)==NS
 base=rgb(S);n=rgb(N);f=base[:700,:3180].astype(np.float32);initial=f.copy()
 # Correct the artificial x2150 cap/wall tone seam on its left side only.
 x=2150
 vd=f[:,x]-f[:,x-1];vd=guided_1d(vd,(f[:,x]+f[:,x-1])/2,4,22)
 vd=np.clip(vd,-24,24)
 vy=1-smooth(np.clip((np.arange(700)-590)/110,0,1))
 wx=smooth(np.clip((np.arange(3180)-1750)/(x-1-1750),0,1));wx[x:]=0
 vertical=np.zeros_like(f)
 for col in range(1750,x):
  v=gaussian_filter1d(vd,max(1,(x-col)/5),axis=0,mode='nearest')
  chrom=f[:,col]-np.mean(f[:,col],axis=1,keepdims=True)
  refch=f[:,x-1]-np.mean(f[:,x-1],axis=1,keepdims=True)
  sim=np.exp(-np.sum((chrom-refch)**2,axis=1)/(35**2))
  vertical[:,col]=v*(vy*wx[col]*sim)[:,None]
 f+=vertical
 # Exact boundary color evidence from actual north last row; never copy its halo geometry.
 delta=n[-1,:3180].astype(np.float32)-f[0]
 delta=guided_1d(delta,(n[-1,:3180].astype(np.float32)+f[0])/2,4,16)
 delta=np.clip(delta,-72,72)
 xx=np.arange(3180);yy=np.arange(700)
 xf=1-smooth(np.clip((xx-3100)/80,0,1))
 # Wide smooth falloff; color only, with chroma similarity protecting other materials below.
 yf=1-smooth(np.clip(yy/520,0,1))
 ch=f-np.mean(f,axis=2,keepdims=True)
 ch0=ch[0:1]
 similar=np.zeros(ch.shape[:2],np.float32)
 for row in range(700):
  guidech=gaussian_filter1d(ch0[0],max(1,row/3),axis=0,mode='nearest')
  chroma=np.sqrt(np.sum((ch[row]-guidech)**2,axis=1))
  similar[row]=np.exp(-(chroma/42)**2)
 # Low-saturation shadows and stone share color family; preserve their native luminance edges.
 alpha=similar*yf[:,None]*xf[None,:]
 field=np.zeros_like(f)
 for row in range(520):
  spread=gaussian_filter1d(delta,max(1,row/3),axis=0,mode='nearest')
  field[row]=spread*alpha[row,:,None]
 f+=field
 out=base.copy();out[:700,:3180]=np.clip(np.rint(f),0,255).astype(np.uint8)
 change=out.astype(np.int16)-base.astype(np.int16)
 assert not np.any(change[700:]) and not np.any(change[:,3180:])
 yy1,xx1=np.nonzero(np.any(change,axis=2));bounds=[int(xx1.min()),int(yy1.min()),int(xx1.max()+1),int(yy1.max()+1)]
 D.mkdir(parents=True,exist_ok=True);np.savez_compressed(D/'rgb-difference-field.npz',delta_rgb_i16=change[:700,:3180],rect_xyxy=[0,0,3180,700],north_boundary_delta_rgb_f32=delta,vertical_delta_rgb_f32=vd,alpha_f16=alpha.astype(np.float16),vertical_field_f16=vertical.astype(np.float16))
 ci=img(D/'candidate.png',out)
 ex=rgb(T/'repairs/north-integrated-v2/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base);ex[115:4211,115:4211]=out
 ei=img(D/'extended-context.png',ex)
 pair=np.concatenate([n,out],axis=0);views=[]
 for i,x0 in enumerate([0,1024,2048,2842],1):
  views.append(dict(img(Q/f'north-wide-{i}.png',pair[3796:4566,x0:x0+1254]),sourceRectInNorthPair=[x0,3796,x0+1254,4566]))
 for name,b in [('north-left-insertion',[750,0,1110,707]),('north-middle-insertion',[1920,0,2250,707]),('north-right-insertion',[3090,0,3430,707]),('north-bottom-left',[800,450,2054,710]),('north-bottom-right',[2054,450,3308,710]),('top-left',[0,0,1254,700])]:
  a,b0,c,d=b;views.append(dict(img(Q/(name+'.png'),out[b0:d,a:c]),sourceRectXYXY=b))
 img(Q/'overview.png',np.array(Image.fromarray(out).resize((1024,1024),Image.Resampling.LANCZOS)))
 save(D/'manifest.json',dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),input=ref(S),immutableNorth=ref(N),candidate=ci,extendedContext=ei,field=ref(D/'rgb-difference-field.npz'),changedBoundsXYXY=bounds,changedPixels=int(np.any(change,axis=2).sum()),maxActualRGBChange=int(np.abs(change).max()),operations=[dict(kind='vertical tone seam x2150 correction',side='left only',xFade=[1750,2149],yFade=[590,700],maximumChannelDelta=24,edgeAware1dRadius=4),dict(kind='actual north boundary RGB-difference field',firstRowEvidence='actual north last row minus candidate first row',maximumChannelDelta=72,yFadeToZero=520,xFade=[3100,3180],materialWeight='continuous chroma similarity sigma42; no hard material mask',edgeAware1dRadius=4)],x3180AndBeyondExact=True,y700AndBeyondExact=True,immutableNorthCurrentSha256=sha(N),geometryResampling=False,imageBlur=False,finalArtUpscaled=False,qa=views,visualReview='pending',formalAccepted=False))
 print(json.dumps(dict(candidate=ci,changedBounds=bounds,maxActualRGBChange=int(np.abs(change).max()))))
def wy0(x):return x[:,None]
if __name__=='__main__':main()


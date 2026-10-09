from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h;import quilt as q
h.O=O/'north';gen=h.ingest('north-locked-return','C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c/exec-399fd125-bffa-472d-90a6-324738e0f410.png')
src=O/'north-joint-candidate-v2.png';a=np.asarray(Image.open(src),np.float32);b=np.asarray(Image.open(gen),np.float32)
Y,X=np.indices((1254,1254));m=(X>=557)&(X<790)&(Y>=480)&(Y<720)
border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));base=a[:,:1254];grad=np.max(abs(base-np.roll(base,1,0))+abs(base-np.roll(base,1,1)),axis=2);rel=border&(grad<30)&(np.max(abs(base-b),axis=2)<60)
w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((base-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-24,24)*np.clip(w*240,0,1)*m[:,:,None]
rep=np.clip(np.rint(b+f),0,255).astype('uint8');arr=a.astype('uint8');arr[:,:1254][m]=rep[m]
mp=O/'north-locked-return-mask.png';rp=O/'north-locked-return-replacement.png';fp=O/'north-locked-return-fields.npz';np.savez_compressed(fp,fields=f)
Image.fromarray(m.astype('uint8')*255).save(mp);h.derived(mp,[gen,src],{'method':'binary narrow x557..790,y480..720 mask; root first557 fully protected'})
Image.fromarray(rep).save(rp);h.derived(rp,[gen,src,mp],{'method':'boundedRGB reliable perimeter','cap':24,'fieldFile':str(fp),'fieldSha256':h.sha(fp),'imageBlur':False,'resampling':False})
dest=O/'north-joint-candidate-v3.png';Image.fromarray(arr).save(dest);h.derived(dest,[src,rp,mp],{'method':'native binary patch; first557columns identical'})
old=np.asarray(Image.open(O/'north-v2-mask.png'));new=old.copy();new[:,:1254]=np.maximum(new[:,:1254],m*255);fp=O/'north-v3-mask.png';Image.fromarray(new.astype('uint8')).save(fp);h.derived(fp,[O/'north-v2-mask.png',mp],{'method':'mask union'})
p=O/'qa-north-v3-1.png';Image.fromarray(arr[:,:1254]).save(p);h.derived(p,[dest],{'method':'native1254review crop'})
print(dest,h.sha(dest))

from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h;import quilt as q
src=O/'north-joint-candidate-v3.png';gen=O/'north/north-locked-return-generated.png'
a=np.asarray(Image.open(src),np.float32);b=np.asarray(Image.open(gen),np.float32);lum=b.mean(2)
points=[]
for x in range(235,842):
 z=int(862-.502*x)-18;score=lum[z:z+36,x]-(lum[z-8:z+28,x]+lum[z+8:z+44,x])/2;y=z+int(np.argmax(score));points.append((x,y))
pm=Image.new('L',(1254,1254));d=ImageDraw.Draw(pm);d.line(points,fill=255,width=22);d.rectangle((495,607,625,666),fill=255);m=np.asarray(pm)>0
base=a[:,:1254];border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));grad=np.max(abs(base-np.roll(base,1,0))+abs(base-np.roll(base,1,1)),axis=2);rel=border&(grad<30)&(np.max(abs(base-b),axis=2)<60)
w=q.smooth(q.smooth(rel[:,:,None].astype('float32')),12);num=q.smooth(q.smooth((base-b)*rel[:,:,None]),12);f=np.clip(num/np.maximum(w,1e-6),-24,24)*np.clip(w*240,0,1)*m[:,:,None]
rep=np.clip(np.rint(b+f),0,255).astype('uint8');arr=a.astype('uint8');arr[:,:1254][m]=rep[m]
mp=O/'north-corner-contour-mask.png';rp=O/'north-corner-contour-replacement.png';fp=O/'north-corner-contour-fields.npz';np.savez_compressed(fp,fields=f,contour=np.asarray(points))
Image.fromarray(m.astype('uint8')*255).save(mp);h.derived(mp,[gen,src],{'method':'22px actualAI plank groove contour corridor from natural endpoint; adjacent tiny wood-paint rectangle','authorizedProtectionException':'root explicitly allowed only existing plank-groove contour into former557 corner protection','sourceResampling':False})
Image.fromarray(rep).save(rp);h.derived(rp,[gen,src,mp],{'method':'boundedRGB reliable perimeter; AI actual pixels held at native geometry','cap':24,'fieldFile':str(fp),'fieldSha256':h.sha(fp),'imageBlur':False,'resampling':False})
dest=O/'north-joint-candidate-v4.png';Image.fromarray(arr).save(dest);h.derived(dest,[src,rp,mp],{'method':'native binary contour patch with root-approved corner edge exception'})
old=np.asarray(Image.open(O/'north-v3-mask.png'));new=old.copy();new[:,:1254]=np.maximum(new[:,:1254],m*255);fp=O/'north-v4-mask.png';Image.fromarray(new.astype('uint8')).save(fp);h.derived(fp,[O/'north-v3-mask.png',mp],{'method':'mask union'})
chg=np.any(arr[:,:1254]!=a[:,:1254].astype('uint8'),axis=2);protected=chg.copy();protected[:,557:]=False
for side,ss in [('north',np.s_[:627,:627]),('self',np.s_[627:1254,:627])]:
 z=chg[ss];im=Image.fromarray(z.astype('uint8')*255);print(side,int(z.sum()),im.getbbox())
rec={'approvedBy':'root collaboration message: relax protection only along existing plank groove to natural endpoint','newContourChangeBBox':Image.fromarray(chg.astype('uint8')*255).getbbox(),'changePixelCount':int(chg.sum()),'previouslyProtectedChangeCount':int(protected.sum()),'previouslyProtectedBBox':Image.fromarray(protected.astype('uint8')*255).getbbox(),'onlyNativeAIRedraw':True}
(O/'corner-protection-exception.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
p=O/'qa-north-v4-1.png';Image.fromarray(arr[:,:1254]).save(p);h.derived(p,[dest],{'method':'native1254review crop'});print(dest,h.sha(dest))

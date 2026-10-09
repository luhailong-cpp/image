import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image
import ai_helper as h
import quilt as q
import integrate_west_v2 as w
O=h.O
h.ingest('west-return-ai-v2',Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c/exec-ad8d3682-2ca2-4026-933f-5e101bb1984d.png'))
inp=O/'west-return-edit-input.png';gen=O/'west-return-ai-v2-generated.png'
a=np.asarray(Image.open(inp).convert('RGB'),np.float32);b=np.asarray(Image.open(gen).convert('RGB'),np.float32)
cost=np.mean(np.minimum(abs(a-b),50)**2,axis=2);Y,X=np.indices((1254,1254));m=np.zeros((1254,1254),bool)
specs={'rail':{'left':[550,580],'right':[710,735],'top':[10,30],'bottom':[210,245]},'leaves':{'left':[570,605],'right':[725,755],'top':[920,950],'bottom':[1200,1250]}}
paths={}
for n,s in specs.items():
 l=w.cut(cost,*s['left']);r=w.cut(cost,*s['right']);t=w.cut(cost.T,*s['top']);d=w.cut(cost.T,*s['bottom']);m|=(X>=l[:,None])&(X<r[:,None])&(Y>=t[None,:])&(Y<d[None,:]);paths[n+'left']=l;paths[n+'right']=r;paths[n+'top']=t;paths[n+'bottom']=d
border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));border[[0,-1],:]=False;border[:,[0,-1]]=False
grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);reliable=border&(grad<35)&(np.max(abs(a-b),axis=2)<35)
weight=q.smooth(q.smooth(reliable[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*reliable[:,:,None]));f=np.clip(num/np.maximum(weight,1e-6),-8,8)*np.clip(weight*240,0,1)*m[:,:,None];rep=np.clip(np.rint(b+f),0,255).astype('uint8')
rp=O/'west-return-replacement.png';mp=O/'west-return-mask.png';fp=O/'west-return-fields.npz'
np.savez_compressed(fp,field=f,**paths);Image.fromarray(rep).save(rp);Image.fromarray((m*255).astype('uint8')).save(mp)
h.derived(mp,[inp,gen],{'method':'two local binary minimum-error masks','ranges':specs});h.derived(rp,[inp,gen,mp],{'method':'bounded additive RGB correction only','cap':8,'fieldFile':str(fp),'fieldSHA':h.sha(fp),'resampling':False,'imageBlur':False})
src=O/'joint-candidate-west-v2.png';joint=Image.open(src).convert('RGB');joint.paste(Image.fromarray(rep),(0,1024),Image.fromarray((m*255).astype('uint8')))
d=O/'joint-candidate-west-final.png';joint.save(d);h.derived(d,[src,rp,mp],{'method':'two binary local native repair masks','origin':[0,1024],'outsideMaskIdentical':True})
mask=Image.open(O/'joint-mask-west-v2.png').convert('L');patch=Image.new('L',mask.size);patch.paste(Image.fromarray((m*255).astype('uint8')),(0,1024));mask=Image.fromarray(np.maximum(np.asarray(mask),np.asarray(patch)))
mm=O/'joint-mask-west-final.png';mask.save(mm);h.derived(mm,[O/'joint-mask-west-v2.png',mp],{'method':'union of binary western repair masks'})
w.export(d,mm,'final')
for n,box in {'rail':(460,1024,800,1310),'leaves':(510,1930,810,2278),'bevel':(790,3720,1254,4096)}.items():
 p=O/f'qa-west-final-{n}.png';joint.crop(box).save(p);h.derived(p,[d],{'nativeCrop':box})

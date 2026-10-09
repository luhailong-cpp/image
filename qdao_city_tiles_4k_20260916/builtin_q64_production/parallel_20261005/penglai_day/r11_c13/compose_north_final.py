import helper as h
import numpy as np
from PIL import Image
R=h.ROOT;p=h.p;P=R/'repairs/north/joint-v2';D=R/'repairs/north/joint-v3';D.mkdir(exist_ok=True)
src=P/'north-joint.png';out=np.asarray(Image.open(src).convert('RGB')).copy();a=np.asarray(Image.open(R/'native/nr3-mask.png').convert('RGB'));before=out[:,2842:].copy();yy,xx=np.indices((1254,1254));m=np.zeros((1254,1254),'float32')
boxes=[([338,585,1280,670],18),([111,209,169,285],10),([163,1090,234,1167],10)]
for box,fade in boxes:
    x0,y0,x1,y1=box;m=np.maximum(m,np.clip(np.minimum(np.minimum(xx-x0,x1-1-xx),np.minimum(yy-y0,y1-1-yy))/fade,0,1))
after=np.round(before*(1-m[:,:,None])+a*m[:,:,None]).astype('uint8');out[:,2842:]=after
np.savez_compressed(D/'nr3-mask-alpha.npz',alpha=m);Image.fromarray(after).save(D/'nr3-final-native.png');p.derived(D/'nr3-final-native.png',[src,R/'native/nr3-mask.png'],{'method':'native ROI repair at joint x2842','boxesWithFeather':boxes,'noScaling':True})
joint=D/'north-joint.png';Image.fromarray(out).save(joint);p.derived(joint,[src,R/'native/nr3-mask.png'],{'method':'native coordinate local AI band and edge repair','boxesWithFeather':boxes,'formalAccepted':False})
old=p.read(P/'integration.json');tiles={}
for tid,item in old['tiles'].items():
    a=np.asarray(Image.open(item['file']).convert('RGB')).copy()
    if tid=='r10_c13':a[3469:]=out[:627]
    else:a[:627]=out[627:]
    f=D/f'{tid}-candidate.png';Image.fromarray(a).save(f);p.derived(f,[item['file'],joint],{'method':'native627 shared boundary replacement','formalAccepted':False});tiles[tid]={'file':str(f),'sha256':p.sha(f),'source':item['source'],'sourceSha256':item['sourceSha256']}
p.write(D/'integration.json',{'at':p.stamp(),'tiles':tiles,'joint':str(joint),'jointSha256':p.sha(joint),'prior':str(P/'integration.json'),'mask':str(D/'nr3-mask-alpha.npz'),'review':'pending native final repair inspection','formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False})
print(tiles)

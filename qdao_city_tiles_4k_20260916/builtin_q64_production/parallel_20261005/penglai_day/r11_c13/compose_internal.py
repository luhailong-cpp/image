import helper as h
import sys,numpy as np
from PIL import Image
R=h.ROOT;p=h.p;D=R/'repairs/internal';sys.path.insert(0,str(D));import quilt as q
plan=p.read(D/'repair-plan.json');src=plan['source'];assert p.sha(src)==plan['sha256'];out=np.asarray(Image.open(src).convert('RGB')).copy();original=out.copy();proof=[]
boxes={'i1':([260,320,1180,1190],40),'i2':([560,410,745,980],24),'i3':([90,350,1175,960],30),'i4':([350,370,720,1030],32),'i5':([315,510,450,750],20)}
def alpha(box,fade):
    y,x=np.indices((1254,1254));x0,y0,x1,y1=box;return np.clip(np.minimum(np.minimum(x-x0,x1-1-x),np.minimum(y-y0,y1-1-y))/fade,0,1).astype('float32')
for j in plan['jobs']:
    n=j['name'];x,y=j['originXY'];f=R/'native'/f'{n}.png';a=np.asarray(Image.open(f).convert('RGB'))
    if n=='i2':
        tiny=np.asarray(Image.open(R/'native/i2-tiny.png').convert('RGB'));t=alpha([643,572,705,668],10);a=np.round(a*(1-t[:,:,None])+tiny*t[:,:,None]).astype('uint8');Image.fromarray(a).save(D/'i2-repaired-native.png');p.derived(D/'i2-repaired-native.png',[f,R/'native/i2-tiny.png'],{'method':'tiny native outline-hole repair exact coordinates','boxLTRB':[643,572,705,668],'feather':10});f=D/'i2-repaired-native.png'
    box,fade=boxes[n];m=alpha(box,fade);before=out[y:y+1254,x:x+1254].copy();after=np.round(before*(1-m[:,:,None])+a*m[:,:,None]).astype('uint8');out[y:y+1254,x:x+1254]=after
    np.savez_compressed(D/f'{n}-alpha.npz',alpha=m);Image.fromarray(after).save(D/f'{n}-composite.png');p.derived(D/f'{n}-composite.png',[src,f],{'method':'native1254crop local repair blend with explicit ROI, no scaling','originXY':[x,y],'boxLTRB':box,'feather':fade})
    proof.append({'name':n,'source':str(f),'sha256':p.sha(f),'originXY':[x,y],'localBoxLTRB':box,'feather':fade,'changedPixels':int(np.any(after!=before,axis=2).sum())})
assert np.array_equal(out[:627],original[:627]),'North frozen anchor was changed'
dest=D/'r11_c13-internal-candidate-v2.png';Image.fromarray(out).save(dest);p.derived(dest,[src]+[x['source']for x in proof],{'method':'five native AI local contour repairs; top627 unchanged','steps':proof,'formalAccepted':False});p.write(D/'integration-v2.json',{'at':p.stamp(),'file':str(dest),'sha256':p.sha(dest),'steps':proof,'top627Unchanged':True,'visualReview':'pending composites/returns','formalAccepted':False});q.qa(out,'v2',dest);print(p.sha(dest))

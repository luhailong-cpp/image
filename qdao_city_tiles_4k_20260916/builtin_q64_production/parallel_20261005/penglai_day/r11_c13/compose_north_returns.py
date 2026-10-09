import helper as h
import numpy as np
from PIL import Image
R=h.ROOT;p=h.p;P=R/'repairs/north/joint-v1';D=R/'repairs/north/joint-v2';Q=D/'qa';D.mkdir(exist_ok=True);Q.mkdir(exist_ok=True)
plan=p.read(P/'return-plan.json');src=plan['source'];assert p.sha(src)==plan['sha256'];out=np.asarray(Image.open(src).convert('RGB')).copy();proof=[]
boxes={'nr1':([400,500,1090,1100],70),'nr2':([537,1000,622,1200],14),'nr3':([350,535,1290,750],42)}
for j in plan['jobs']:
    n=j['name'];x,y=j['originXY'];f=R/'native'/f'{n}.png';a=np.asarray(Image.open(f).convert('RGB'));yy,xx=np.indices((1254,1254));box,fade=boxes[n];x0,y0,x1,y1=box;m=np.clip(np.minimum(np.minimum(xx-x0,x1-1-xx),np.minimum(yy-y0,y1-1-yy))/fade,0,1).astype('float32')
    before=out[:,x:x+1254].copy();after=np.round(before*(1-m[:,:,None])+a*m[:,:,None]).astype('uint8');out[:,x:x+1254]=after
    np.savez_compressed(D/f'{n}-alpha.npz',alpha=m);Image.fromarray(after).save(Q/f'{n}-composite.png');p.derived(Q/f'{n}-composite.png',[src,f],{'method':'native coordinate local AI ROI repair, no scaling','originXY':[x,y],'boxLTRB':box,'feather':fade})
    proof.append({'name':n,'source':str(f),'sha256':p.sha(f),'originXY':[x,y],'boxLTRB':box,'feather':fade,'changedPixels':int(np.any(after!=before,axis=2).sum())})
joint=D/'north-joint.png';Image.fromarray(out).save(joint);p.derived(joint,[src]+[t['source']for t in proof],{'method':'three local native AI return repairs','steps':proof,'formalAccepted':False})
old=p.read(P/'integration.json');tiles={}
for tid,item in old['tiles'].items():
    a=np.asarray(Image.open(item['file']).convert('RGB')).copy()
    if tid=='r10_c13':a[3469:]=out[:627]
    else:a[:627]=out[627:]
    f=D/f'{tid}-candidate.png';Image.fromarray(a).save(f);p.derived(f,[item['file'],joint],{'method':'native627 shared boundary replacement','formalAccepted':False});tiles[tid]={'file':str(f),'sha256':p.sha(f),'source':item['source'],'sourceSha256':item['sourceSha256']}
for i in range(4):Image.fromarray(out[:,i*1024:(i+1)*1024]).save(Q/f's{i+1}.png')
p.write(D/'integration.json',{'at':p.stamp(),'tiles':tiles,'joint':str(joint),'jointSha256':p.sha(joint),'steps':proof,'prior':str(P/'integration.json'),'review':'pending native returns','formalAccepted':False})
print(tiles)

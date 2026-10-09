import helper as h
import importlib.util
import numpy as np
from PIL import Image
R=h.ROOT; p=h.p; B=R.parent; N=R/'repairs/north'; D=N/'joint-v1'; Q=D/'qa'
D.mkdir(exist_ok=True);Q.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('seamhelper',B/'r10_c12/repairs/north/build_joint.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
state=p.read(N/'state.json'); northfile=state['north']['source']; southfile=R/'repairs/internal/r11_c13-internal-candidate-v2.png'
assert p.sha(northfile)==state['north']['sha256']
assert p.sha(state['southTop627Source'])==state['southSha256']
base=q.arr(N/'north-input.png'); north=q.arr(northfile).copy(); south=q.arr(southfile).copy()
assert np.array_equal(south[:627],q.arr(state['southTop627Source'])[:627])
assert np.array_equal(base,np.concatenate([north[3469:],south[:627]],axis=0))
paths=[R/'native'/f'n{i}.png' for i in range(1,5)];sources=[q.arr(f) for f in paths]
assert all(a.shape==(1254,1254,3) for a in sources)
canvas=np.zeros_like(base);owner=np.zeros(base.shape[:2],np.uint8);canvas[:,:1254]=sources[0];owner[:,:1254]=1
cuts={};fields={}
for i,(start,width) in enumerate([(1024,230),(2048,230),(2842,460)],1):
    left=canvas[:,start:start+width];right=sources[i][:,:width];c=q.path_cut(left,right,35,width-25,width//2)
    ref=sources[i].copy();ref[:,:width]=left
    corrected,field=q.color_return(ref,sources[i],c,'x',support=140,cap=12)
    fields[f'segment{i+1}']=field;cuts[f'segment{i+1}']=c
    use=np.arange(width)[None,:]>=c[:,None]
    canvas[:,start:start+width]=np.where(use[:,:,None],corrected[:,:width],left)
    owner[:,start:start+width]=np.where(use,i+1,owner[:,start:start+width])
    canvas[:,start+width:start+1254]=corrected[:,width:];owner[:,start+width:start+1254]=i+1
upper=q.path_cut(base,canvas,90,400,240,'y');lower=q.path_cut(canvas,base,980,1190,1100,'y')
canvas,fields['upper']=q.color_return(base,canvas,upper,'y',cap=12)
canvas,fields['lower']=q.color_return(base,canvas,lower,'y',cap=12)
cuts.update(upper=upper,lower=lower)
yy=np.arange(1254)[:,None];mask=(yy>=upper[None,:])&(yy<lower[None,:])
out=np.where(mask[:,:,None],canvas,base)
joint=D/'north-joint.png';Image.fromarray(out).save(joint)
Image.fromarray(canvas).save(D/'north-quilt.png');Image.fromarray(owner).save(D/'source-owner.png');Image.fromarray(mask.astype('uint8')*255).save(D/'native-mask.png')
np.savez_compressed(D/'cuts.npz',**cuts);np.savez_compressed(D/'fields.npz',**fields)
op={'method':'Native same-coordinate binary minimum-error source selection and outer return paths; additive RGB field cap12/channel per stage; no scaling, warping or image blur','fields':str(D/'fields.npz'),'fieldMaxEach':{k:float(abs(v).max())for k,v in fields.items()},'cuts':str(D/'cuts.npz'),'mask':str(D/'native-mask.png'),'formalAccepted':False}
p.derived(joint,[N/'north-input.png']+paths,op)
north[3469:]=out[:627];south[:627]=out[627:]
records={}
for tid,a,src in [('r10_c13',north,northfile),('r11_c13',south,southfile)]:
    f=D/f'{tid}-candidate.png';Image.fromarray(a).save(f);p.derived(f,[src,joint],{'method':'native627 shared boundary replacement; no scaling','formalAccepted':False})
    records[tid]={'file':str(f),'sha256':p.sha(f),'source':str(src),'sourceSha256':p.sha(src)}
for i in range(4):Image.fromarray(out[:,i*1024:(i+1)*1024]).save(Q/f's{i+1}.png')
for i,at in enumerate([1139,2163,3072],1):Image.fromarray(out[:,at-180:at+180]).save(Q/f'junction{i}.png')
Image.fromarray(out).resize((1638,502),Image.Resampling.LANCZOS).save(D/'preview.png')
p.write(D/'integration.json',{'at':p.stamp(),'tiles':records,'joint':str(joint),'jointSha256':p.sha(joint),'globalOriginXY':state['globalOriginXY'],'operation':op,'review':'pending native visual review','formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False})
print(records)

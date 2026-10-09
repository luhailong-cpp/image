from pathlib import Path
from PIL import Image
import sys, importlib.util
import numpy as np
R=Path(__file__).resolve().parent; B=R.parents[2]; sys.path.insert(0,str(B)); import production as p
spec=importlib.util.spec_from_file_location('northbuild',B/'r10_c12/repairs/north/build_joint.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
arr=helper.arr; cut=helper.path_cut; color=helper.color_return
D=R/'joint-v1';D.mkdir(exist_ok=True);Q=D/'qa';Q.mkdir(exist_ok=True)
for direction,letter in [('north','n'),('west','w')]:
    base=arr(R/'references'/f'{direction}-joint-input.png')
    if direction=='west':base=base.transpose(1,0,2)
    srcpaths=[R/'native'/f'{letter}{i}.png' for i in range(1,5)]
    srcs=[arr(f) for f in srcpaths]
    if direction=='west':srcs=[a.transpose(1,0,2) for a in srcs]
    canvas=np.zeros_like(base);owner=np.zeros(base.shape[:2],np.uint8)
    canvas[:,:1254]=srcs[0];owner[:,:1254]=1
    cuts={};fields={}
    for i,start in enumerate([1024,2048,2842],1):
        width=[230,230,460][i-1];left=canvas[:,start:start+width];right=srcs[i][:,:width]
        c=cut(left,right,35,width-25,width//2)
        if direction=='west' and i==3:
            # w3 eliminated the spurious half mortar; adopt w4 after the entire unwanted added groove ends.
            c[:]=448
        ref=srcs[i].copy();ref[:,:width]=left
        corrected,field=color(ref,srcs[i],c,'x',support=140,cap=12)
        fields[f'segment{i+1}']=field;cuts[f'segment{i+1}']=c
        use=np.arange(width)[None,:]>=c[:,None]
        canvas[:,start:start+width]=np.where(use[:,:,None],corrected[:,:width],left)
        owner[:,start:start+width]=np.where(use,i+1,owner[:,start:start+width])
        canvas[:,start+width:start+1254]=corrected[:,width:];owner[:,start+width:start+1254]=i+1
    upper=cut(base,canvas,90,400,240,'y');lower=cut(canvas,base,980,1190,1100,'y')
    canvas,fields['upper']=color(base,canvas,upper,'y',cap=12)
    canvas,fields['lower']=color(base,canvas,lower,'y',cap=12)
    beginning=cut(base,canvas,557,755,630)
    canvas,fields['beginning']=color(base,canvas,beginning,'x',support=150,cap=12)
    yy,xx=np.mgrid[:1254,:4096]
    mask=(yy>=upper[None,:])&(yy<lower[None,:])&(xx>=beginning[:,None])
    result=np.where(mask[:,:,None],canvas,base)
    cuts.update({'upper':upper,'lower':lower,'beginning':beginning})
    if direction=='west':
        result=result.transpose(1,0,2);canvas=canvas.transpose(1,0,2);mask=mask.T;owner=owner.T
    f=D/f'{direction}-joint.png';Image.fromarray(result).save(f)
    Image.fromarray(canvas).save(D/f'{direction}-quilt.png');Image.fromarray(mask.astype(np.uint8)*255).save(D/f'{direction}-mask.png');Image.fromarray(owner).save(D/f'{direction}-owner.png')
    np.savez_compressed(D/f'{direction}-cuts.npz',**cuts);np.savez_compressed(D/f'{direction}-fields.npz',**fields)
    p.derived(f,[R/'references'/f'{direction}-joint-input.png']+srcpaths,{'method':'native same-coordinate binary minimum-error ownership, RGB field cap12 per stage, no rescale/warp/blur/feather; original first557px preserved','cuts':str(D/f'{direction}-cuts.npz'),'fields':str(D/f'{direction}-fields.npz'),'fieldMaxEach':{k:float(abs(v).max())for k,v in fields.items()},'formalAccepted':False})
    for i in range(4):
        part=result[:,i*1024:(i+1)*1024] if direction=='north' else result[i*1024:(i+1)*1024]
        Image.fromarray(part).save(Q/f'{direction}-s{i+1}.png')
    for i,at in enumerate([1139,2163,3290],1):
        part=result[:,at-180:at+180]if direction=='north'else result[at-180:at+180]
        Image.fromarray(part).save(Q/f'{direction}-junction{i}.png')
    part=result[:,430:820]if direction=='north'else result[430:820]
    Image.fromarray(part).save(Q/f'{direction}-corner-return.png')
    p.write(D/f'{direction}-record.json',{'file':str(f),'sha256':p.sha(f),'mask':str(D/f'{direction}-mask.png'),'maskSha256':p.sha(D/f'{direction}-mask.png'),'changedPixels':int(np.any(result!=arr(R/'references'/f'{direction}-joint-input.png'),axis=2).sum()),'sourceNative':[{'file':str(x),'sha256':p.sha(x)}for x in srcpaths],'formalAccepted':False,'review':'pending actual native visual review'})
    print(direction,p.sha(f))


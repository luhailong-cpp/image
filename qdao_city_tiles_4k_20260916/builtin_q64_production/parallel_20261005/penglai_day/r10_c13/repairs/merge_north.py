from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageFilter
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(R));import seam_local as s
from merge_local import apply
from integrate_ai import path
N=T.parent/'tiles/current/r09_c13-candidate-v4b.png';S=R/'r10_c13-internal-ai-v3.png'
def run():
    north=s.arr(N);south=s.arr(S);joint=np.concatenate([north[-627:],south[:627]],axis=0);sources=[N,S]
    tone=R/'north-right-tone-strip.png';joint[371:883,2370:]=s.arr(tone)[:,2370:];sources.append(tone)
    for name,x in [('north-left-roof',0),('north-left-foliage',768),('north-table',1152),('north-right-stair',2048),('north-right-floor',2842)]:
        rep=R/(name+'-replacement.png');mp=R/(name+'-mask.png');mask=np.asarray(Image.open(mp))>0
        oldtarget=s.arr(R/(name+'-target.png'));context=joint[:,x:x+1254].copy();difference=context-oldtarget
        if name=='north-right-floor':
            new=s.arr(rep);cost=np.mean(abs(context-new),axis=2)
            g1=np.diff(context,axis=1,prepend=context[:,:1]);g2=np.diff(new,axis=1,prepend=new[:,:1]);cost+=np.mean(abs(g1-g2),axis=2)*2
            pp=np.full(1254,100,dtype=np.int16);mask &= np.arange(1254)[None,:]>=pp[:,None]
            mp=R/'north-right-floor-actual-neighbor-mask-v4.png';Image.fromarray(mask.astype('uint8')*255).save(mp);s.h.p.derived(mp,[rep,R/'north-right-stair-matched-replacement-v3.png'],{'method':'fixed ownership cut100px from native left border to retain the entire incoming paving corner and bevel','xRange':[20,420],'gradientWeight':2,'noResampling':True});np.savez_compressed(R/'north-right-floor-actual-neighbor-path-v4.npz',path=pp)
        # Only match the previous repair's color change. No change is made where
        # the mask's prior context is still the exact target used for its AI call.
        weight=np.clip((1-np.asarray(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.GaussianBlur(24)),dtype=np.float32)/255)*2,0,1)
        field=np.clip(s.smooth2(difference,r=16),-12,12)*weight[:,:,None]*mask[:,:,None]
        if name=='north-right-floor':
            leftweight=np.clip(1-(np.arange(1254)-100)/96,0,1)[None,:,None]**2
            direct=np.clip(s.smooth2(context-s.arr(rep),r=12),-18,18)*leftweight*mask[:,:,None]
            field=np.where(np.arange(1254)[None,:,None]<196,direct,field)
        matched=s.arr(rep)+field
        np.savez_compressed(R/(name+'-neighbor-return-fields-v3.npz'),field=field)
        matchedp=R/(name+'-matched-replacement-v3.png');s.save(matched,matchedp,[rep,mp,R/(name+'-target.png')]+sources,{'method':'additional bounded RGB correction only for changed previous-repair context at binary ownership perimeter','maxRGB':float(abs(field).max()),'imageBlur':None,'maskGaussianRadius':24,'RGBDifferenceBoxRadius':16,'fieldFile':str(R/(name+'-neighbor-return-fields-v3.npz'))})
        apply(joint,matched,mask,(x,0));sources.extend([matchedp,mp])
    north[-627:]=joint[:627];south[:627]=joint[627:]
    for name,im,base in [('r09_c13-north-revised-v7.png',north,N),('r10_c13-combined-v10.png',south,S)]:
        dest=R/name;s.save(im,dest,sources,{'method':'binary source masks plus bounded RGB north shared-edge correction; all art remains native','formalAccepted':False});delta=np.max(abs(im-s.arr(base)),axis=2)>0;mp=R/(Path(name).stem+'-changed-mask.png');Image.fromarray(delta.astype('uint8')*255).save(mp);s.h.p.derived(mp,[dest,base],{'method':'exact pixel change mask against source'})
    s.save(joint,R/'north-combined-joint-v7.png',sources,{'method':'native joint627px per side for review'})
    board=np.zeros((1280,1024,3))
    for i in range(4):board[i*320:(i+1)*320]=joint[467:787,i*1024:(i+1)*1024]
    s.save(board,R/'north-combined-shared-v7.png',[R/'north-combined-joint-v7.png'],{'method':'four native320px shared-edge crops stacked, no resampling'})
    for start in [0,1024,2048]:
        #1254 context includes every return in width and complete changed band.
        s.save(joint[:,start:start+1254],R/f'north-combined-returns-{start}-v7.png',[R/'north-combined-joint-v7.png'],{'method':'native1254px return context'})
    s.save(joint[:,2842:4096],R/'north-combined-returns-2842-v7.png',[R/'north-combined-joint-v7.png'],{'method':'native1254px return context'})
    s.qa(south,'combined-v10',R/'r10_c13-combined-v10.png')
    s.h.p.write(R/'combined-v10-manifest.json',{'northBase':str(N),'northBaseSha256':s.h.p.sha(N),'northCandidate':str(R/'r09_c13-north-revised-v7.png'),'northSha256':s.h.p.sha(R/'r09_c13-north-revised-v7.png'),'southCandidate':str(R/'r10_c13-combined-v10.png'),'southSha256':s.h.p.sha(R/'r10_c13-combined-v10.png'),'formalAccepted':False,'clientAccepted':False})
if __name__=='__main__':run()







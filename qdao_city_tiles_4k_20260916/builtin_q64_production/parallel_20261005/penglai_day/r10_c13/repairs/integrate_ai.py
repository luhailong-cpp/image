from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(R));import seam_local as s
def path(cost):
    n,w=cost.shape;dp=cost[0].copy();back=np.zeros((n,w),np.int16)
    for i in range(1,n):
        opts=np.stack([np.r_[1e9,dp[:-1]],dp,np.r_[dp[1:],1e9]])
        idx=opts.argmin(axis=0);back[i]=idx-1;dp=cost[i]+opts[idx,np.arange(w)]
    pp=np.zeros(n,np.int16);pp[-1]=dp.argmin()
    for i in range(n-1,0,-1):pp[i-1]=pp[i]+back[i,pp[i]]
    return pp
def region(name,top=None,bottom=None,left=None,right=None):
    orig=s.arr(R/(name+'-target.png'));srcp=R/'native'/(name+'.png');new=s.arr(srcp);hh,ww=orig.shape[:2]
    cost=np.mean(abs(orig-new),axis=2)
    yy,xx=np.indices((hh,ww));mask=np.ones((hh,ww),bool);distance=np.full((hh,ww),1000.,dtype=np.float32);paths={}
    for side,ran in [('top',top),('bottom',bottom),('left',left),('right',right)]:
        if ran is None:continue
        start,end=ran
        trans=side in ['top','bottom']
        cc=cost.T[:,start:end] if trans else cost[:,start:end]
        pp=path(cc)+start;paths[side]=pp
        dd=(yy-pp[None,:]) if trans else (xx-pp[:,None])
        if side in ['bottom','right']:dd=-dd
        mask &= dd>=0;distance=np.minimum(distance,dd)
    if name=='north-left-foliage':
        permitted=Image.new('L',(ww,hh),0)
        ImageDraw.Draw(permitted).polygon([(0,0),(1253,0),(1253,1253),(850,1253),(850,950),(760,900),(650,875),(560,850),(450,800),(325,730),(210,635),(100,525),(0,410)],fill=255)
        mask &= np.asarray(permitted)>0
    color=s.smooth2(orig-new,r=16);field=np.clip(color,-10,10)*np.clip(1-distance[:,:,None]/96,0,1)**2
    field[~mask]=0;replacement=np.clip(new+field,0,255)
    rep=R/(name+'-replacement.png');s.save(replacement,rep,[srcp,R/(name+'-target.png')],{'method':'AI native repair with bounded RGB return field; no geometry transformation','maxAdditiveRGB':float(abs(field).max()),'fieldFile':str(R/(name+'-integration-fields.npz'))})
    np.savez_compressed(R/(name+'-integration-fields.npz'),field=field,**paths)
    mp=R/(name+'-mask.png');Image.fromarray(mask.astype('uint8')*255).save(mp);s.h.p.derived(mp,[srcp,R/(name+'-target.png')],{'method':'binary minimal-error native source ownership paths','bands':{'top':top,'bottom':bottom,'left':left,'right':right}})
    result=np.where(mask[:,:,None],replacement,orig)
    s.save(result,R/(name+'-integrated-review.png'),[srcp,R/(name+'-target.png'),mp],{'method':'preview native source repair composition, no resizing'})
    return replacement,mask
if __name__=='__main__':
    name=sys.argv[1]
    if name=='paving-y3072':region(name,top=(400,510),bottom=(780,920))
    elif name=='roof-x1024':region(name,left=(380,500),right=(1120,1230))
    elif name=='wall-y3072':region(name,top=(170,310),bottom=(980,1150))
    elif name=='north-table':region(name,top=(300,430),bottom=(1100,1190),left=(470,550),right=None)
    elif name=='north-left-roof':region(name,top=(300,450),bottom=(1030,1170),right=(1080,1200))
    elif name=='north-left-foliage':region(name,top=(300,430),bottom=(960,1130),left=(70,210),right=(930,1070))
    elif name=='north-right-stair':region(name,top=(300,450),bottom=(980,1160),left=(50,180),right=(1090,1200))
    elif name=='north-right-floor':region(name,top=(300,450),bottom=(1080,1210))

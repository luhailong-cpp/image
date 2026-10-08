from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(R));import seam_local as s
N=T.parent/'tiles/current/r09_c13-candidate-v4b.png';S=R/'r10_c13-internal-ai-v3.png'
def prepare(name,x):
    out=R/(name+'-target.png');im=Image.new('RGB',(1254,1254));im.paste(Image.open(N).crop((x,3469,x+1254,4096)),(0,0));im.paste(Image.open(S).crop((x,0,x+1254,627)),(0,627));im.save(out)
    s.h.p.derived(out,[N,S],{'method':'native joint crop','northBoxLTRB':[x,3469,x+1254,4096],'southBoxLTRB':[x,0,x+1254,627],'resampling':None})
    detail='golden rounded roof and every existing curved tile rim' if name.endswith('roof') else ('existing grey stone staircase, stone rim, warm wood tabletop and its bevel' if 'stair' in name else ('cream paving bevels and existing grey stone stair risers; also remove the vertical pigment seam at x230 below y627' if 'floor' in name else 'foliage silhouettes, leaves, trunks, golden roof edge and warm wood'))
    prompt='Use case: precise-object-edit. Image 1 is the exact native EDIT TARGET. Image 2 is the approved PRIMARY PAINTING STYLE, never copy UI. Across horizontal y627 there is an accidental tile splice. Repair that splice in the '+detail+'. Unify material hue and illumination across it. Reconnect existing contours as continuous edges with the same endpoints. Keep exact camera, crop, scale, geometry design, count and density of every object. Change only the narrow horizontal splice vicinity, restoring original pixels by y430 and y840; preserve outer150px frame where not crossed by seam. No extra details, objects, panels, seams or lines. Bright clean rounded full Taoist Q handpaint style, restrained texture, warm highlights, clean cool shadows. No blur, sharpen halos, noise, text, UI, border or watermark. Same square crop.'
    (R/(name+'.prompt.txt')).write_text(prompt,encoding='utf8');call={'prompt':prompt,'referenced_image_paths':[out.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False};s.h.p.write(R/(name+'.call.json'),call)
def tone():
    n=s.arr(N);so=s.arr(S);full=np.concatenate([n[3840:],so[:256]],axis=0);x0=2370
    part=full[:,x0:].copy();jump=part[256:260].mean(axis=0)-part[252:256].mean(axis=0)
    gx=np.max(abs(np.diff(part[252:260],axis=1)),axis=(0,2));good=np.r_[gx<9,True]
    xx=np.arange(len(good))
    for c in range(3):jump[:,c]=np.interp(xx,xx[good],jump[good,c])
    correction=np.clip(s.smooth1(jump,radius=8)/2,-14,14)
    yd=np.arange(512)-255.5;weight=np.maximum(0,1-abs(yd)/160)**2
    xfade=np.clip(np.arange(part.shape[1])/64,0,1)
    field=correction[None,:,:]*weight[:,None,None]*np.where(yd[:,None,None]<0,1,-1)*xfade[None,:,None]
    part+=field;full[:,x0:]=part
    np.savez_compressed(R/'north-right-tone-fields.npz',field=field)
    s.save(full,R/'north-right-tone-strip.png',[N,S],{'method':'geometry unchanged; bounded additive RGB seam illumination correction','x0':x0,'jointY0':3840,'maxRGB':float(abs(field).max()),'normalFalloff':160,'tangentSmoothing':17,'sourceShift':0,'imageBlur':None})
    board=np.zeros((640,1024,3));board[:320]=full[96:416,2048:3072];board[320:]=full[96:416,3072:4096];s.save(board,R/'north-right-tone-native-review.png',[R/'north-right-tone-strip.png'],{'method':'two native1024x320 crops stacked'})
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare('north-left-roof',0);prepare('north-left-foliage',768)
    elif sys.argv[1]=='right':
        N=R/'r09_c13-north-revised-v1.png';S=R/'r10_c13-combined-v4.png';prepare('north-right-stair',2048);prepare('north-right-floor',2842)
    elif sys.argv[1]=='tone':tone()

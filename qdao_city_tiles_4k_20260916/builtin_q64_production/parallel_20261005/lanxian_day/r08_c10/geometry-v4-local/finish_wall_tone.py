"""Local seam-tone equalization after new geometry; cumulative RGB delta is bounded."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
from finish_wall import taper,sha,save
OUT=Path(__file__).resolve().parent;TILE=OUT.parent
def warp_saved(a,p):
 z=np.load(p);fx=z['flow_x'];fy=z['flow_y'];active=(abs(fx)+abs(fy))>1e-7;y,x=np.where(active);x0,x1=x.min(),x.max()+1;y0,y1=y.min(),y.max()+1
 yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32);w=cv2.remap(a,xx+fx[y0:y1,x0:x1],yy+fy[y0:y1,x0:x1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101);o=a.copy();m=active[y0:y1,x0:x1];o[y0:y1,x0:x1][m]=w[m];return o
def main():
 stage=OUT/'core4096.png';assert sha(stage)=='7c4bef697cd47cba4d2f7126be7eaa82b952a0e9d05a6ce460b589a341ad5fc1'
 a=np.array(Image.open(stage).convert('RGB'));initial=np.array(Image.open(TILE/'geometry-v3-local/core4096.png').convert('RGB'))
 baseline=np.array(Image.open(TILE/'geometry-v2/core4096.png').convert('RGB'))
 baseline=warp_saved(baseline,TILE/'geometry-v3-local/outer-bevel-flow.npz');baseline=warp_saved(baseline,OUT/'wall-column-flow.npz')
 box=[2894,2018,2992,2078];x0,y0,x1,y1=box;ys=np.arange(y0,y1);xs=np.arange(x0,x1);field=np.zeros((y1-y0,x1-x0,3),np.float32);parts={};features=[]
 specs=[('shadow_plane',2924.2399,-.10347,-10,16),('diagonal_ink',2953.6572,-.82728,-8,8),('pillar_ink',2972.0567,.01088,-8,10)]
 for name,c,s,lo,hi in specs:
  us=np.arange(lo-4,hi+5,dtype=float);times=np.arange(-5,5)+.5;profiles=[]
  for t in times:
   y=int(2047.5+t);xx=c+s*t+us;profiles.append(np.array([np.interp(xx,np.arange(4096),a[y,:,ch]) for ch in range(3)]).T)
  profiles=np.array(profiles);up=np.polyfit(times[:5],profiles[:5].reshape(5,-1),1)[1].reshape(len(us),3);down=np.polyfit(times[5:],profiles[5:].reshape(5,-1),1)[1].reshape(len(us),3)
  delta=cv2.GaussianBlur((down-up).astype(np.float32),(1,3),sigmaX=0,sigmaY=.7)
  piece=np.zeros_like(field)
  for i,y in enumerate(ys):
   u=xs-(c+s*(y-2047.5));cross=taper(u,lo-4,lo,hi,hi+4);along=taper(np.array([y]),y0,2043,2053,y1-1)[0]
   if name=='shadow_plane':
    # Do not recolor steep silhouette pixels to imitate a displacement.
    gradient=abs(np.gradient(a[y].mean(1)))[xs];cross*=np.clip((7-gradient)/4,0,1)
    cross*=np.clip((abs(xs-(2953.6572-.82728*(y-2047.5)))-8)/5,0,1)
   values=np.array([np.interp(u,us,delta[:,ch]) for ch in range(3)]).T
   piece[i]=values*(.5 if y<2048 else -.5)*cross[:,None]*along
  parts[name+'_requested_rgb']=piece;field+=piece
  features.append({'name':name,'alignedCenterAt2047_5':c,'slope':s,'transverseFullRange': [lo,hi],'profileExtrapolationRows': [2043,2044,2045,2046,2047,2048,2049,2050,2051,2052],'estimatedStepPerChannelMax':np.max(abs(delta),axis=0).tolist(),'profileSmoothingOnly':'sigma .7; image RGB pixels are never blurred'})
 old=a[y0:y1,x0:x1].astype(np.int16);ref=baseline[y0:y1,x0:x1].astype(np.int16)
 requested=np.rint(old.astype(float)+field);low=np.maximum(0,ref-12);high=np.minimum(255,ref+12);new=np.clip(requested,low,high).astype(np.uint8)
 active=np.any(abs(field)>1e-7,axis=2);new[~active]=old[~active].astype(np.uint8);after=a.copy();after[y0:y1,x0:x1]=new
 actual=new.astype(np.int16)-old;cumulative=after.astype(np.int16)-baseline.astype(np.int16);assert abs(cumulative).max()<=12
 changed=np.any(a!=after,axis=2);assert np.array_equal(after[:,:2880],a[:,:2880])
 full_field=np.zeros((4096,4096,3),np.float32);full_field[y0:y1,x0:x1]=field
 fp=OUT/'wall-column-tone.npz';np.savez_compressed(fp,requested_rgb=field,applied_rgb=actual,support_box=np.array(box),**parts)
 output=save('core4096.png',after);mask=save('tone-support-mask.png',(changed*255).astype(np.uint8))
 allchanged=np.any(initial!=after,axis=2);save('changed-pixels.png',(allchanged*255).astype(np.uint8))
 boards=[]
 for name,b in [('wall-column-entire',[2400,1920,3328,2176]),('right-wall-detail',[2872,1984,3024,2112]),('post-detail',[2960,1984,3260,2112]),('local-shadow-detail',[2904,2016,2952,2080])]:
  first=Image.fromarray(initial).crop(b);second=Image.fromarray(after).crop(b);board=Image.new('RGB',(first.width,first.height*2+40),(28,28,28));d=ImageDraw.Draw(board);d.text((3,3),'BEFORE v3',fill='white');board.paste(first,(0,20));d.text((3,first.height+23),'AFTER v4',fill='white');board.paste(second,(0,first.height+40));info=save('qa/'+name+'-before-after.png',board);info['coreBoxLTRB']=b;info['scale']=1;boards.append(info)
 yp,xp=np.where(changed)
 report={'createdAt':datetime.now(timezone.utc).isoformat(),'inputGeometryStageSha256':'7c4bef697cd47cba4d2f7126be7eaa82b952a0e9d05a6ce460b589a341ad5fc1','output':output,'toneSupportRectangleLTRB':box,'actualToneBoundsLTRB':[int(xp.min()),int(yp.min()),int(xp.max()+1),int(yp.max()+1)],'changedPixels':int(changed.sum()),'maxNewAppliedRGB':np.max(abs(actual),axis=(0,1)).tolist(),'maxCumulativeRGB':np.max(abs(cumulative),axis=(0,1)).tolist(),'cumulativeReference':'geometry-v2 toneless baseline transported through identical v3 and v4 fields; prior geometry is not applied again to tonal input','toneField':{'file':str(fp),'sha256':sha(fp)},'toneMask':mask,'features':features,'qaBoards':boards,'RGBBlur':False,'geometryAlteredByTone':False,'previousLeftContoursByteIdentical':True,'formalAccepted':False,'visualInspectionPerformed':False,'script':{'file':str(Path(__file__)),'sha256':sha(__file__)}}
 (OUT/'tone-processing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'output':output,'cumulativeMax':report['maxCumulativeRGB'],'newMax':report['maxNewAppliedRGB'],'changedPixels':report['changedPixels']}))
if __name__=='__main__':main()

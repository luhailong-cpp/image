"""One new bounded local registration pass on geometry-v3; no prior flow replay."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
OUT=Path(__file__).resolve().parent
TILE=OUT.parent
SOURCE=TILE/'geometry-v3-local/core4096.png'
EXPECTED='5114535256dd9f7a713464e7284f089c3805f75d253f5ac7175d4f66f389c483'
BOX=[2880,2012,3010,2090]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,a):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);im=a if isinstance(a,Image.Image) else Image.fromarray(a);im.save(p)
 return {'file':str(p),'sha256':sha(p),'pixels':list(im.size)}
def taper(t,a,b,c,d):
 t=np.asarray(t,float);v=np.ones_like(t);left=t<b;right=t>c
 v[left]=.5-.5*np.cos(np.pi*np.clip((t[left]-a)/(b-a),0,1))
 v[right]=.5+.5*np.cos(np.pi*np.clip((t[right]-c)/(d-c),0,1));return v
def crossing(g,y,guess,level,radius=10):
 x0=int(guess)-radius;v=g[y,x0:x0+2*radius+1];ks=np.where((v[:-1]>level)&(v[1:]<=level))[0]
 if not len(ks):raise ValueError((y,guess,level))
 ps=np.array([x0+k+(v[k]-level)/(v[k]-v[k+1]) for k in ks]);return float(ps[np.argmin(abs(ps-guess))])
def center(g,y,guess):
 x0=int(guess)-6;v=g[y,x0:x0+13];k=int(np.argmin(v))
 if k==0 or k==len(v)-1:raise ValueError(('center',y,k))
 return x0+k+.5*(v[k-1]-v[k+1])/(v[k-1]-2*v[k]+v[k+1])
def remap(a,dx,dy):
 x0,y0,x1,y1=BOX;yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32);active=(abs(dx)+abs(dy))>1e-7
 warped=cv2.remap(a,xx+dx,yy+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101);out=a.copy();out[y0:y1,x0:x1][active]=warped[active];return out
def main():
 assert sha(SOURCE)==EXPECTED
 before=np.array(Image.open(SOURCE).convert('RGB'));g=before.mean(2);x0,y0,x1,y1=BOX
 ys=np.arange(y0,y1);xs=np.arange(x0,x1);dt=ys-2047.5
 specs=[('shadow_plane',2012,2038,2058,2084,190,14,4),('diagonal_bottom',2035,2043,2057,2076,120,11,5),('pillar_outline',2016,2039,2057,2089,None,12,5)]
 parts={};numer=np.zeros((len(ys),len(xs)),float);denom=np.zeros_like(numer);metadata=[]
 for name,start,full0,full1,end,level,radius,plateau in specs:
  valid=(ys>=start)&(ys<=end);tracks=np.zeros(len(ys));t=ys[valid]-2047.5
  for i,y in enumerate(ys):
   if not valid[i]:continue
   if name=='shadow_plane':guess=2924-.09*(y-2048);tracks[i]=crossing(g,y,guess,level,14)
   elif name=='diagonal_bottom':guess=2954-.84*(y-2048);tracks[i]=crossing(g,y,guess,level,8)
   else:tracks[i]=center(g,y,2972)
  stable=valid&(abs(dt)>=4)&(abs(dt)<=min(12,2047.5-start-1))
  upper=stable&(dt<0);lower=stable&(dt>0)
  fu=np.polyfit(dt[upper],tracks[upper],1);fl=np.polyfit(dt[lower],tracks[lower],1)
  fit=(fu+fl)/2;target=np.polyval(fit,dt)
  raw=tracks-target;displacement=np.clip(raw,-4,4);along=taper(ys,start,full0,full1,end)*valid
  weight=np.array([taper(xs,tx-radius,tx-plateau,tx+plateau,tx+radius) for tx in target])*along[:,None]
  local_displacement=np.broadcast_to(displacement[:,None],weight.shape).copy()
  if name=='pillar_outline':
   anchors=np.zeros((len(ys),3));anchors[:,1]=tracks
   for i,y in enumerate(ys):
    if not valid[i]:continue
    v=g[y,2964:2982];k=int(round(tracks[i]))-2964
    leftlevel=(v[k]+v[0])/2;rightlevel=(v[k]+v[-1])/2
    lk=np.where((v[:k]>leftlevel)&(v[1:k+1]<=leftlevel))[0]
    rk=np.where((v[k:-1]<rightlevel)&(v[k+1:]>=rightlevel))[0]
    if len(lk):j=int(lk[-1]);anchors[i,0]=2964+j+(v[j]-leftlevel)/(v[j]-v[j+1])
    else:anchors[i,0]=tracks[i]-1.5
    if len(rk):j=int(rk[0])+k;anchors[i,2]=2964+j+(rightlevel-v[j])/(v[j+1]-v[j])
    else:anchors[i,2]=tracks[i]+1.5
   afits=np.array([(np.polyfit(dt[upper],anchors[upper,k],1)+np.polyfit(dt[lower],anchors[lower,k],1))/2 for k in range(3)])
   atarget=np.array([np.polyval(f,dt) for f in afits]).T
   for i in range(len(ys)):
    if valid[i]:local_displacement[i]=np.interp(xs,atarget[i],np.clip(anchors[i]-atarget[i],-4,4))
   parts['pillar_source_three_anchors']=anchors;parts['pillar_target_three_anchors']=atarget
  part=local_displacement*weight;numer+=part;denom+=weight
  parts[name+'_dx_uncombined']=part.astype(np.float32);parts[name+'_weight']=weight.astype(np.float32);parts[name+'_source_contour']=tracks;parts[name+'_target_contour']=target
  metadata.append({'name':name,'sourceContourThreshold':level,'yRange':[start,end],'crossRadius':radius,'plateauRadius':plateau,'fitUpper':fu.tolist(),'fitLower':fl.tolist(),'targetFit':fit.tolist(),'rawCentralDx':[float(raw[ys==2047][0]),float(raw[ys==2048][0])],'maximumRawRequestedDx':float(abs(raw[valid&(abs(dt)<8)]).max()),'fieldCappedAt':4,'classification':'Existing contour registration; no missing structure'})
 dx=(numer/np.maximum(1,denom)).astype(np.float32);dy=np.zeros_like(dx);assert abs(dx).max()<=4
 for name,*_ in specs:
  parts[name+'_dx_applied']=(parts[name+'_dx_uncombined']/np.maximum(1,denom)).astype(np.float32)
  parts[name+'_dy_applied']=np.zeros_like(dx)
  parts[name+'_actual_support_mask']=abs(parts[name+'_dx_applied'])>1e-7
 after=remap(before,dx,dy)
 fullx=np.zeros((4096,4096),np.float32);fullx[y0:y1,x0:x1]=dx;fully=np.zeros_like(fullx);active=abs(fullx)>1e-7;changed=np.any(before!=after,axis=2)
 assert not np.any(changed&~active);assert np.array_equal(before[:,:2880],after[:,:2880])
 output=save('core4096.png',after)
 flow=OUT/'wall-column-flow.npz';np.savez_compressed(flow,flow_x=fullx,flow_y=fully,local_dx=dx,local_dy=dy,support_box=np.array(BOX),**parts)
 masks=[save('support-mask.png',(active*255).astype(np.uint8)),save('taper-weight.png',np.pad(np.rint(np.minimum(denom,1)*255).astype(np.uint8),((y0,4096-y1),(x0,4096-x1)))),save('changed-pixels.png',(changed*255).astype(np.uint8))]
 boards=[]
 for name,box in [('wall-column-entire',[2400,1920,3328,2176]),('right-wall-detail',[2872,1984,3024,2112]),('post-detail',[2960,1984,3260,2112]),('local-shadow-detail',[2904,2016,2952,2080])]:
  a=Image.fromarray(before).crop(box);b=Image.fromarray(after).crop(box);board=Image.new('RGB',(a.width,a.height*2+40),(28,28,28));draw=ImageDraw.Draw(board)
  draw.text((3,3),'BEFORE v3',fill='white');board.paste(a,(0,20));draw.text((3,a.height+23),'AFTER v4',fill='white');board.paste(b,(0,a.height+40));info=save('qa/'+name+'-before-after.png',board);info['coreBoxLTRB']=box;info['scale']=1;boards.append(info)
 yp,xp=np.where(active)
 report={'createdAt':datetime.now(timezone.utc).isoformat(),'source':{'file':str(SOURCE),'sha256':EXPECTED},'output':output,'operation':'One new local horizontal displacement on v3 current RGB pixels; prior flows not replayed','supportRectangleLTRB':BOX,'actualSupportLTRB':[int(xp.min()),int(yp.min()),int(xp.max()+1),int(yp.max()+1)],'maxDx':float(abs(dx).max()),'maxDy':0,'minimumMappingJacobian':float((1+np.gradient(dx,axis=1)).min()),'changedPixels':int(changed.sum()),'outsideSupportByteIdentical':True,'previousLeftContoursByteIdentical':True,'priorFlowReapplied':False,'RGBBlur':False,'newRGBToneField':False,'resampling':{'method':'cv2.INTER_LINEAR','subpixel':True,'newPasses':1,'onlyNonzeroFieldPixelsWritten':True},'features':metadata,'flow':{'file':str(flow),'sha256':sha(flow),'convention':'Output samples current input(x+dx,y+dy)'},'masks':masks,'qaBoards':boards,'formalAccepted':False,'visualInspectionPerformed':False,'sourceUnchanged':sha(SOURCE)==EXPECTED,'script':{'file':str(Path(__file__)),'sha256':sha(__file__)}}
 (OUT/'processing.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'output':output,'maxDx':report['maxDx'],'minJacobian':report['minimumMappingJacobian'],'features':metadata},ensure_ascii=False))
if __name__=='__main__':main()

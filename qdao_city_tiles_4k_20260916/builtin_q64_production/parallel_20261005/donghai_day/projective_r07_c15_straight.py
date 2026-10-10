"""Register straight existing beams with a planar homography; never bend their edges."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';sys.path.insert(0,str(D/'python-deps'));import cv2
def runs(row):
 v=row.astype(float);warm=v[:,0]>v[:,2]+20;d=np.diff(np.r_[False,warm,False].astype(int));return [(s,e) for s,e in zip(np.where(d==1)[0],np.where(d==-1)[0]) if e-s>30]
def main(name):
 F=D/'south-straight'/name;p=np.asarray(Image.open(F/'edited-native.png').convert('RGB'));target=F/('fixed-context.png' if name=='s4-frame-final' else 'composition-reference.png');t=np.asarray(Image.open(target).convert('RGB'))
 ys=np.arange(841,981);pe=[];te=[]
 for y in ys:
  if name=='s3':
   def ed(a,pred):
    v=a[y].astype(float);lo=int(pred-20);hi=int(pred+20);return [np.argmin(v.mean(1)[lo:hi])+lo,runs(a[y])[0][1]]
   pe.append(ed(p,552-(y-841)*0.88));te.append(ed(t,585-(y-841)*1.06))
  else:pe.append(runs(p[y])[1]);te.append(runs(t[y])[1])
 ps=[np.polyfit(ys,np.array(pe)[:,k],1) for k in [0,1]];ts=[np.polyfit(ys,np.array(te)[:,k],1) for k in [0,1]]
 def quad(c):return np.array([[np.polyval(c[0],841),841],[np.polyval(c[1],841),841],[np.polyval(c[1],980),980],[np.polyval(c[0],980),980]],np.float32)
 H=cv2.getPerspectiveTransform(quad(ts),quad(ps))
 Y,X=np.mgrid[:956,:1254].astype(np.float32);coords=np.stack([X,Y],axis=-1).reshape(-1,1,2);mapped=cv2.perspectiveTransform(coords,H).reshape(956,1254,2);mx,my=mapped[:,:,0],mapped[:,:,1]
 warped=cv2.remap(p,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
 if name=='s4-frame-final':
  le=np.polyval(ts[0],Y);ri=np.polyval(ts[1],Y);sle=np.polyval(ps[0],Y);sri=np.polyval(ps[1],Y)
  core=(X>=np.minimum(le,sle)-12)&(X<=np.maximum(ri,sri)+12)&(Y>=700)
  dil=cv2.dilate(core.astype(np.uint8),np.ones((61,61),np.uint8));dist=cv2.distanceTransform(dil,cv2.DIST_L2,3);alpha=np.clip(dist/25,0,1);alpha[Y<700]=0
  # Physical occlusion: the main broad diagonal beam remains the original native object.
  beam_edges=np.array([runs(p[y])[0][1] for y in ys]);bc=np.polyfit(ys,beam_edges,1);main_end=np.polyval(bc,Y);alpha[X<main_end+2]=0
  warped=np.rint(p[:956]*(1-alpha[:,:,None])+warped*alpha[:,:,None]).astype(np.uint8)
 else:alpha=np.ones((956,1254),np.float32)
 Image.fromarray(warped).save(F/'projective-upper.png')
 out=warped.astype(float);w=np.linspace(0,1,115);w=w*w*(3-2*w);out[841:956]=out[841:956]*(1-w[:,None,None])+t[841:956]*w[:,None,None];out=np.rint(out).astype('uint8');Image.fromarray(out).save(F/'halo-matched-upper.png')
 np.savez_compressed(F/'straight-registration.npz',map_x=mx,map_y=my,apply_alpha_f32=alpha.astype(np.float32))
 meta={'operation':'Single planar projective registration of existing straight timber surfaces. Projective maps preserve straight lines; no row-wise nonlinear offset.','sourceSha256':hashlib.sha256((F/'edited-native.png').read_bytes()).hexdigest(),'targetSha256':hashlib.sha256(target.read_bytes()).hexdigest(),'targetToSourceHomography':H.tolist(),'sourceEdgeLinearFits':np.asarray(ps).tolist(),'targetEdgeLinearFits':np.asarray(ts).tolist(),'fitRows':[841,981],'maxCoordinateDisplacementOnAppliedPixels':float(np.sqrt((mx-X)**2+(my-Y)**2)[alpha>0.5].max()),'sampling':'bilinear; no upscale','application':'entire source patch' if name=='s3' else 'existing canopy frame and <=60px adjoining cloth only, original main beam/rope anchor preserved by occlusion mask','authoritativeHaloTransition':{'rows':[841,956],'smoothstep':True,'lastRowExact':True}}
 (F/'straight-registration.json').write_text(json.dumps(meta,indent=2))
 south=np.array(Image.open(R/'r08_c15/output/r08_c15.png').convert('RGB'));x=2048 if name=='s3' else 2842;sh=Image.new('RGB',(1254,700));sh.paste(Image.fromarray(out[-500:]),(0,0));sh.paste(Image.fromarray(south[:200,x:x+1254]),(0,500));sh.save(D/'qa-probes'/f'{name}-projective-common-edge.png');print(name,meta['maxCoordinateDisplacementOnAppliedPixels'])
if __name__=='__main__':main(sys.argv[1])


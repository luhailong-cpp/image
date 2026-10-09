from pathlib import Path
import json, hashlib, importlib.util, sys, shutil
from datetime import datetime, timezone
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'tools/deps'))
import cv2
HELPER=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tools/mechanical_join.py')
spec=importlib.util.spec_from_file_location('join',HELPER);mj=importlib.util.module_from_spec(spec);spec.loader.exec_module(mj)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def arr(p):return np.array(Image.open(p).convert('RGB'))
def save(p,a):Image.fromarray(a).save(p)
source=R/'assembly-registered/r10_c12-candidate.png'
baseline=arr(source)
assert sha(source)=='715f763d6e9116ac3dbdc9148d7246e85e6a394d94e52659de0da758fef04a0c'
draftp=R/'rows/row3/p34-draft.png';leftp=R/'rows/row3/p33.png';oldp=R/'rows/row3/p34.png'
draft=arr(draftp);left=arr(leftp)[:,1024:1254];old=arr(oldp)
h,w=draft.shape[:2];yy,xx=np.mgrid[:h,:w].astype(np.float32)
ctx=draft.copy();ctx[:,:230]=left
f=cv2.calcOpticalFlowFarneback(cv2.cvtColor(ctx[:,:230],cv2.COLOR_RGB2GRAY),cv2.cvtColor(draft[:,:230],cv2.COLOR_RGB2GRAY),None,0.5,4,41,5,7,1.5,0)
f=cv2.GaussianBlur(f,(0,0),4)
edge=np.median(f[:,210:226],axis=1)
edge=cv2.GaussianBlur(edge[:,None,:],(0,0),3)[:,0,:]
edge=np.clip(edge,-6,6)
weight=smooth((430-xx)/200)*(xx>=230)
flow=edge[:,None,:]*weight[:,:,None]
aligned=cv2.remap(draft,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# Boundary colour field is estimated from actual neighbouring native pixels;
# only this low-frequency difference field is smoothed, never the artwork.
delta=(left[:,229].astype(np.float32)-aligned[:,230].astype(np.float32))
delta=cv2.GaussianBlur(delta[:,None,:],(0,0),2)[:,0,:]
delta=np.clip(delta,-24,24)
tone=delta[:,None,:]*smooth((470-xx)/240)[:,:,None]*(xx>=230)[:,:,None]
fixed=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
fixed[:,:230]=left
assert np.array_equal(fixed[:,:230],old[:,:230])
assert np.array_equal(fixed[:,470:],old[:,470:])
save(O/'p34-native-corrected.png',fixed);np.save(O/'p34.flow.npy',flow);np.save(O/'p34.colorCorrection.npy',tone)
save(O/'p34.mask.png',np.uint8((xx>=230)&(xx<470))*255)
def assemble(override=None):
 canvas=np.zeros((4326,4326,3),np.uint8)
 for rr in range(4):
  for cc in range(4):
   name=f'p{rr+1}{cc+1}';patch=(override if name=='p34' and override is not None else arr(R/f'rows/row{rr+1}/{name}.png'))
   x,y=cc*1024,rr*1024;context=patch.copy();edges=[]
   if rr:context[:230]=canvas[y:y+230,x:x+1254];edges.append('top')
   if cc:context[:,:230]=canvas[y:y+1254,x:x+230];edges.append('left')
   if not edges:canvas[y:y+1254,x:x+1254]=patch;continue
   d=np.full((1254,1254),1254.)
   if rr:d=np.minimum(d,yy)
   if cc:d=np.minimum(d,xx)
   mask=np.uint8(np.rint(smooth((d-99)/32)*255))
   merged,_,_,_=mj.registered_join(context,patch,mask,edges=edges,max_shift=6,flow_inner=230,flow_full=130,tone_inner=330,tone_full=140)
   canvas[y:y+1254,x:x+1254]=merged
 return canvas[115:4211,115:4211]
repro=assemble();assert np.array_equal(repro,baseline),'Original assembly did not reproduce'
repaired=assemble(fixed)
changed=np.any(repaired!=baseline,axis=2);cy,cx=np.nonzero(changed);pbox=(int(cx.min()),int(cy.min()),int(cx.max()+1),int(cy.max()+1))
save(O/'p34-merge.png',repaired[pbox[1]:pbox[3],pbox[0]:pbox[2]])
leafhost=Path('C:/Users/luyua/.codex/generated_images/01a10bb7-4da4-7553-abb9-125e7fe01ccc/exec-d6d5d1cd-7dac-495d-8a01-2898d23d3aba.png')
leafp=O/'leaf-repair-native.png';shutil.copyfile(leafhost,leafp)
leaf=arr(leafp);target=arr(O/'leaf-edit-target.png');assert leaf.shape==target.shape==(1254,1254,3)
hsv=cv2.cvtColor(target,cv2.COLOR_RGB2HSV)
material=((hsv[:,:,0]>=24)&(hsv[:,:,0]<=100)&(hsv[:,:,1]>25)).astype(np.uint8)
distance=cv2.distanceTransform(material,cv2.DIST_L2,5)
alpha=smooth((xx-260)/60)*smooth((610-xx)/120)*smooth((yy-290)/50)*smooth((950-yy)/80)*smooth((distance-2)/12)
mask=np.uint8(np.rint(alpha*255));alpha=mask.astype(np.float32)/255
mixed=np.clip(np.rint(target*(1-alpha[:,:,None])+leaf*alpha[:,:,None]),0,255).astype(np.uint8)
save(O/'leaf.mask.png',mask)
assert np.array_equal(mixed[mask==0],target[mask==0])
sy,sx=np.nonzero(mask);lbox=(int(sx.min()+768),int(sy.min()+1536),int(sx.max()+1+768),int(sy.max()+1+1536))
lx0,ly0,lx1,ly1=lbox
repaired[ly0:ly1,lx0:lx1]=mixed[ly0-1536:ly1-1536,lx0-768:lx1-768]
save(O/'leaf-merge.png',repaired[ly0:ly1,lx0:lx1])
qa=[]
for label,x,ya,yb in [('p34-full',3187,1800,3400),('leaf-full',1139,1720,2440)]:
 # Native strip divided into native 800px lengths; no resizing.
 length=yb-ya;parts=(length+799)//800
 sheet=Image.new('RGB',(800,400*parts))
 for i in range(parts):
  box=(x-200,ya+i*800,x+200,min(yb,ya+(i+1)*800))
  im=Image.fromarray(repaired).crop(box).transpose(Image.Transpose.ROTATE_90)
  sheet.paste(im,(0,i*400))
 p=O/(label+'.png');sheet.save(p);qa.append({'file':str(p),'sha256':sha(p),'scale':1,'rotation90':True,'nativeStripXYXY':[x-200,ya,x+200,yb],'actuallyViewed':False})
boxes=[(1024-160,2048-160,1024+160,2048+160),(3072-160,2048-160,3072+160,2048+160),(3072-160,3072-160,3072+160,3072+160)]
sheet=Image.new('RGB',(960,320))
for i,box in enumerate(boxes):sheet.paste(Image.fromarray(repaired).crop(box),(i*320,0))
p=O/'junctions-after.png';sheet.save(p);qa.append({'file':str(p),'sha256':sha(p),'scale':1,'boxesXYXY':boxes,'actuallyViewed':False})
# Return boundaries: native 96px bands around each proposed replacement rectangle.
for label,box in [('leaf',lbox),('p34',pbox)]:
 x0,y0,x1,y1=box;ims=[];bxs=[(x0-48,y0-48,x1+48,y0+48),(x0-48,y1-48,x1+48,y1+48),(x0-48,y0-48,x0+48,y1+48),(x1-48,y0-48,x1+48,y1+48)]
 for i,b in enumerate(bxs):
  im=Image.fromarray(repaired).crop(b)
  if i>=2:im=im.transpose(Image.Transpose.ROTATE_90)
  for start in range(0,im.width,1000):ims.append(im.crop((start,0,min(start+1000,im.width),96)))
 sh=Image.new('RGB',(1000,len(ims)*96))
 for i,im in enumerate(ims):sh.paste(im,(0,96*i))
 p=O/(label+'-returns.png');sh.save(p);qa.append({'file':str(p),'sha256':sha(p),'scale':1,'boundaryBoxesXYXY':bxs,'actuallyViewed':False})
leafrecord={'file':str(leafp),'sha256':sha(leafp),'pixels':[1254,1254],'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','originalToolOutputPath':str(leafhost),'originalToolOutputSha256':sha(leafhost),'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':json.loads((O/'leaf-repair.call.json').read_text())['submittedParameters'],'actualModel':None,'actualQuality':None,'references':[dict(ref(O/'leaf-edit-target.png'),role='exact geometry edit target native crop from assembly'),dict(ref(Path('D:/work/image/designs/gameplay-ui/04-guild.png')),role='main approved style')],'selectedWholeImage':False,'selectedViaMask':str(O/'leaf.mask.png'),'unverifiedReason':'Host-managed builtin tool exposes and returns no model or quality identifiers.'}
write(O/'leaf-repair-native.png.generation.json',leafrecord)
write(O/'repair-manifest.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'baseCandidate':ref(source),'basePixelsReproducedExactly':True,'status':'pending_native_visual_QA','rootOutputModified':False,'algorithmFile':str(Path(__file__).resolve()),'algorithmSha256':sha(__file__),'helper':{'file':str(HELPER),'sha256':sha(HELPER)},'repairs':[{'id':'p34','file':str(O/'p34-merge.png'),'sha256':sha(O/'p34-merge.png'),'mergeRectXYXY':pbox,'globalMergeRectXYXY':[pbox[0]+45056,pbox[1]+36864,pbox[2]+45056,pbox[3]+36864],'inputs':[ref(draftp),ref(leftp),ref(oldp)],'kind':'existing_native_overlap_registration_and_local_colour_field_then_exact_reassembly','preservedNativeLeftStripXYXY':[0,0,230,1254],'nativeAffectedRectXYXY':[230,0,470,1254],'maximumAllowedShiftPixels':6,'actualMaxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),'actualMaxColorCorrectionRGB':np.abs(tone).max(axis=(0,1)).tolist(),'artworkBlurred':False,'scale':1,'mask':ref(O/'p34.mask.png'),'flow':{'file':str(O/'p34.flow.npy'),'sha256':sha(O/'p34.flow.npy')},'colorField':{'file':str(O/'p34.colorCorrection.npy'),'sha256':sha(O/'p34.colorCorrection.npy')},'actualModel':None,'actualQuality':None},{'id':'leaf','file':str(O/'leaf-merge.png'),'sha256':sha(O/'leaf-merge.png'),'mergeRectXYXY':lbox,'globalMergeRectXYXY':[lx0+45056,ly0+36864,lx1+45056,ly1+36864],'inputs':[ref(O/'leaf-edit-target.png'),ref(leafp)],'kind':'native_builtin_leaf_seam_repaint_selected_with_material_mask','editTargetCropXYXY':[768,1536,2022,2790],'nativeGeneratedSize':[1254,1254],'resampling':False,'actualMaxShiftXY':[0,0],'actualMaxColorCorrectionRGB':[0,0,0],'mask':ref(O/'leaf.mask.png'),'maskZeroPixelsUnchanged':True,'scale':1,'actualModel':None,'actualQuality':None}],'qa':qa,'mergeRule':'Paste repair PNGs at their mergeRectXYXY top-left without resize. Base candidate SHA bound above. Both are south of y256 and do not overwrite root north correction. Root owns final merging.'})
print(json.dumps({'p34Rect':pbox,'leafRect':lbox,'p34MaxShift':np.abs(flow).max(axis=(0,1)).tolist(),'p34MaxColor':np.abs(tone).max(axis=(0,1)).tolist(),'qaFiles':[x['file'] for x in qa]},ensure_ascii=False))

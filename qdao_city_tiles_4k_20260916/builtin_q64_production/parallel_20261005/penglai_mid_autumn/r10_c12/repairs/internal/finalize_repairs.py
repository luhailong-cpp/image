from pathlib import Path
import json, hashlib, sys, shutil
from datetime import datetime, timezone
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'tools/deps'));import cv2
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def arr(p):return np.array(Image.open(p).convert('RGB'))
def save(p,a):Image.fromarray(a).save(p)
source=R/'assembly-registered/r10_c12-candidate.png';base=arr(source);repaired=base.copy()
assert sha(source)=='715f763d6e9116ac3dbdc9148d7246e85e6a394d94e52659de0da758fef04a0c'
old=json.loads((O/'repair-manifest.json').read_text());write(O/'mechanical-rejected.json',dict(old,status='rejected',reason='Row-varying boundary colour field produced horizontal streaks; no mechanical output selected for merge.'))
repairs=[];yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
host=Path('C:/Users/luyua/.codex/generated_images/01a10bb7-4da4-7553-abb9-125e7fe01ccc/exec-73a322d4-bdda-41f0-8cf5-b800f7ca569c.png')
shutil.copyfile(host,O/'p34-local-native.png')
for label,origin,srcname in [('leaf',(768,1536),'leaf-repair-native.png'),('p34',(2842,1850),'p34-local-native.png')]:
 target=arr(O/(label+'-edit-target.png'));generated=arr(O/srcname);assert target.shape==generated.shape==(1254,1254,3)
 if label=='leaf':mask=np.array(Image.open(O/'leaf.mask.png'))
 else:mask=np.uint8(np.rint(smooth((xx-245)/55)*smooth((480-xx)/70)*smooth((yy-130)/70)*smooth((1254-yy)/54)*255));save(O/'p34-local.mask.png',mask)
 alpha=mask.astype(np.float32)/255;mixed=np.clip(np.rint(target*(1-alpha[:,:,None])+generated*alpha[:,:,None]),0,255).astype(np.uint8)
 assert np.array_equal(mixed[mask==0],target[mask==0])
 sy,sx=np.nonzero(mask);x0,y0,x1,y1=(int(sx.min()+origin[0]),int(sy.min()+origin[1]),int(sx.max()+1+origin[0]),int(sy.max()+1+origin[1]))
 repaired[y0:y1,x0:x1]=mixed[y0-origin[1]:y1-origin[1],x0-origin[0]:x1-origin[0]]
 dest=O/(label+'-merge.png');save(dest,repaired[y0:y1,x0:x1])
 repairs.append({'id':label,**ref(dest),'mergeRectXYXY':[x0,y0,x1,y1],'globalMergeRectXYXY':[x0+45056,y0+36864,x1+45056,y1+36864],'inputs':[ref(O/(label+'-edit-target.png')),ref(O/srcname)],'kind':'native_builtin_local_seam_repaint_selected_with_alpha_mask','editTargetCropXYXY':[origin[0],origin[1],origin[0]+1254,origin[1]+1254],'nativeGeneratedSize':[1254,1254],'mask':ref(O/('leaf.mask.png' if label=='leaf' else 'p34-local.mask.png')),'maskZeroPixelsUnchanged':True,'resampling':False,'maximumAppliedMechanicalShiftPixels':0,'actualAppliedMechanicalShiftXY':[0,0],'mechanicalColorFieldApplied':False,'actualAppliedMechanicalColorCorrectionRGB':[0,0,0],'generativeGeometryChangeAssessment':'visual check required; zero mechanical displacement does not assert that every generated contour is pixel-identical','scale':1,'actualModel':None,'actualQuality':None,'formalAccepted':False})
qa=[]
for label,x,ya,yb in [('p34-full',3187,1800,3400),('leaf-full',1139,1720,2440)]:
 parts=(yb-ya+799)//800;sheet=Image.new('RGB',(800,400*parts));boxes=[]
 for i in range(parts):
  box=(x-200,ya+i*800,x+200,min(yb,ya+(i+1)*800));boxes.append(box)
  sheet.paste(Image.fromarray(repaired).crop(box).transpose(Image.Transpose.ROTATE_90),(0,i*400))
 p=O/(label+'.png');sheet.save(p);qa.append(dict(ref(p),scale=1,rotation90=True,boxesXYXY=boxes,actuallyViewed=False))
boxes=[(864,1888,1184,2208),(2912,1888,3232,2208),(2912,2912,3232,3232)];sheet=Image.new('RGB',(960,320))
for i,box in enumerate(boxes):sheet.paste(Image.fromarray(repaired).crop(box),(i*320,0))
p=O/'junctions-after.png';sheet.save(p);qa.append(dict(ref(p),scale=1,boxesXYXY=boxes,actuallyViewed=False))
for repair in repairs:
 label=repair['id'];x0,y0,x1,y1=repair['mergeRectXYXY'];ims=[];bxs=[(x0-48,y0-48,x1+48,y0+48),(x0-48,y1-48,x1+48,y1+48),(x0-48,y0-48,x0+48,y1+48),(x1-48,y0-48,x1+48,y1+48)]
 for i,b in enumerate(bxs):
  im=Image.fromarray(repaired).crop(b)
  if i>=2:im=im.transpose(Image.Transpose.ROTATE_90)
  for start in range(0,im.width,1000):ims.append(im.crop((start,0,min(start+1000,im.width),96)))
 sh=Image.new('RGB',(1000,len(ims)*96))
 for i,im in enumerate(ims):sh.paste(im,(0,i*96))
 p=O/(label+'-returns.png');sh.save(p);qa.append(dict(ref(p),scale=1,boundaryBoxesXYXY=bxs,actuallyViewed=False))
record={'file':str(O/'p34-local-native.png'),'sha256':sha(O/'p34-local-native.png'),'pixels':[1254,1254],'generatedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','originalToolOutputPath':str(host),'originalToolOutputSha256':sha(host),'configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':json.loads((O/'p34-local.call.json').read_text())['submittedParameters'],'actualModel':None,'actualQuality':None,'references':[dict(ref(O/'p34-edit-target.png'),role='exact native geometry edit target'),dict(ref(Path('D:/work/image/designs/gameplay-ui/04-guild.png')),role='main approved style')],'selectedWholeImage':False,'selectedViaMask':str(O/'p34-local.mask.png'),'unverifiedReason':'Host-managed builtin; model and quality selectors and result metadata unavailable.'}
write(O/'p34-local-native.png.generation.json',record)
for label,origin in [('p34',(2842,1850)),('leaf',(768,1536))]:
 write(O/(label+'-edit-target.png.generation.json'),dict(ref(O/(label+'-edit-target.png')),kind='exact_native_crop',source=ref(source),cropXYXY=[origin[0],origin[1],origin[0]+1254,origin[1]+1254],resampling=False,scale=1,actualModel=None,actualQuality=None))
write(O/'repair-manifest.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'baseCandidate':ref(source),'status':'pending_native_visual_QA','rootOutputModified':False,'algorithmFile':str(Path(__file__).resolve()),'algorithmSha256':sha(__file__),'repairs':repairs,'qa':qa,'rejectedMechanicalTrial':str(O/'mechanical-rejected.json'),'mergeRule':'Paste each merge PNG at mergeRectXYXY top-left without resize. All outside pixels remain base candidate. Both rectangles are south of y256; root owns final merge with north-corrected output.','formalAccepted':False})
for d in repairs:print(json.dumps({k:d[k] for k in ['id','file','sha256','mergeRectXYXY']},ensure_ascii=False))

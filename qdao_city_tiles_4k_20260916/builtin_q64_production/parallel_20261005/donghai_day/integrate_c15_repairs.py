"""Validate and integrate c15 native repair patches without resampling.

Default writes a review candidate only. --commit requires saved visual approval.
All art outside explicit insertion masks remains byte-for-byte identical.
"""
from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageFilter
import assembly_r08_c15 as a
import integrate_west as joint

R=Path(__file__).resolve().parent;T=R/'r08_c15';D=T/'repairs/consolidated'
if '--broad' in sys.argv:D=T/'repairs/consolidated-broad'
if '--color' in sys.argv:D=T/'repairs/consolidated-color'
S=T/'output/r08_c15.png';BASE='41cd6b8daffcee9e67069688f5b3d5150fbf7576975545ee2287cac44201f50b'
M=D/'masks';Q=D/'qa';C=D/'candidate.png';EX=D/'extended-context.png'
sha=a.sha;load=a.load_json;js=a.save_json;save=a.save_image
def rgb(p):
 with Image.open(p) as im:
  im.load()
  if 'A' in im.getbands():assert im.getextrema()[-1]==(255,255)
  return np.asarray(im.convert('RGB')).copy()
def raw(x):return hashlib.sha256(x.tobytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def cut(x,b):return x[b[1]:b[3],b[0]:b[2]]
def valid_patch(p):
 r=load(Path(str(p)+'.generation.json'));assert sha(p)==r['sha256']
 assert [r['width'],r['height']]==[1254,1254] and r['route']=='builtin'
 assert r['actualModel'] is None and r['actualQuality'] is None
 assert r['submittedParameters']['model'] is None and r['submittedParameters']['quality'] is None
 assert r['resizedAfterGeneration'] is False and r['finalArtUpscaled'] is False
 assert sha(r['prompt'])==r['promptSha256']
 assert r['evidence']['toolResultSha256']==sha(p)
 rawpath=Path(r['evidence']['toolResultSourcePath'])
 if rawpath.exists():assert sha(rawpath)==sha(p)
 for e in r['references']:assert sha(e['file'])==e['sha256'] and e['role']
 return rgb(p),dict(ref(p),record=ref(Path(str(p)+'.generation.json')))
def seam(earlier,later,orient,box,name):
 result,entry=joint.join_overlap(earlier,later,orient,box,name,FN)
 SEAMS.append(entry)
 return result,np.asarray(Image.open(entry['maskPng']['file'])).copy()
def join(patches,starts,orient,x0,y0,label):
 out=patches[0].copy()
 for i,nxt in enumerate(patches[1:],1):
  start=starts[i];axis=1 if orient=='vertical' else 0;ov=out.shape[axis]-start
  if axis==1:
   mixed,_=seam(out[:,-ov:],nxt[:,:ov],orient,[x0+start,y0,x0+start+ov,y0+out.shape[0]],f'{label}-{i}-{i+1}')
   out=np.concatenate((out[:,:-ov],mixed,nxt[:,ov:]),axis=1)
  else:
   mixed,_=seam(out[-ov:],nxt[:ov],orient,[x0,y0+start,x0+out.shape[1],y0+start+ov],f'{label}-{i}-{i+1}')
   out=np.concatenate((out[:-ov],mixed,nxt[ov:]),axis=0)
 return out
def rect_alpha(base,patch,box,edge,label,boundary_full=()):
 h,w=patch.shape[:2];alpha=np.full((h,w),255,np.uint8);e=min(edge,(w-1)//2,(h-1)//2)
 x0,y0,x1,y1=box
 for side in ('left','right','top','bottom'):
  if side in boundary_full:continue
  if side=='left':
   _,m=seam(base[:,:e],patch[:,:e],'vertical',[x0,y0,x0+e,y1],label+'-left');alpha[:,:e]=np.minimum(alpha[:,:e],m)
  elif side=='right':
   _,m=seam(patch[:,-e:],base[:,-e:],'vertical',[x1-e,y0,x1,y1],label+'-right');alpha[:,-e:]=np.minimum(alpha[:,-e:],255-m)
  elif side=='top':
   _,m=seam(base[:e],patch[:e],'horizontal',[x0,y0,x1,y0+e],label+'-top');alpha[:e]=np.minimum(alpha[:e],m)
  else:
   _,m=seam(patch[-e:],base[-e:],'horizontal',[x0,y1-e,x1,y1],label+'-bottom');alpha[-e:]=np.minimum(alpha[-e:],255-m)
 return alpha
def insert(image,patch,box,edge,label,eligibility=None,rects=None):
 before=cut(image,box).copy();h,w=patch.shape[:2];assert before.shape==patch.shape
 if rects is None:alpha=rect_alpha(before,patch,box,edge,label)
 else:
  alpha=np.zeros((h,w),np.uint8)
  for i,b in enumerate(rects):
   local=[b[0]-box[0],b[1]-box[1],b[2]-box[0],b[3]-box[1]]
   allowed=('bottom',) if b[3]==4096 else ()
   m=rect_alpha(cut(before,local),cut(patch,local),b,edge,f'{label}-roi{i+1}',allowed)
   v=cut(alpha,local);np.maximum(v,m,out=v)
 if eligibility is not None:
  assert eligibility.shape==alpha.shape and set(np.unique(eligibility)).issubset({0,255})
  alpha[eligibility==0]=0
 correction=None
 if '--color' in sys.argv:
  original_patch=patch;patch,correction=match_boundary_color(before,patch,alpha,label)
 after=a.blend(before,patch,alpha);image[box[1]:box[3],box[0]:box[2]]=after
 full=np.zeros((4096,4096),np.uint8);full[box[1]:box[3],box[0]:box[2]]=alpha
 GLOBAL_MASK[:]=np.maximum(GLOBAL_MASK,full)
 info=save(M/(label+'-insertion-alpha.png'),Image.fromarray(alpha))
 entry={'id':label,'rectXYXY':box,'edgeSearchPixels':edge,'alpha':info,'intendedRepairRectsXYXY':rects,'changedPixels':int(np.any(before!=after,axis=2).sum()),'exactOriginalAtAlphaZero':bool(np.array_equal(before[alpha==0],after[alpha==0])),'eligibilityMaskApplied':eligibility is not None,'localBoundaryColorMatch':correction}
 assert entry['exactOriginalAtAlphaZero'];INSERTIONS.append(entry)

def match_boundary_color(before,patch,alpha,label):
 """Match low-frequency boundary drift; never filter or warp either art image."""
 def category(x):
  f=x.astype(np.int16);return np.where((f[:,:,2]>f[:,:,0]+15)&(f[:,:,1]>f[:,:,0]+5),1,np.where((f[:,:,0]>f[:,:,2]+15)&(f[:,:,0]>f[:,:,1]+4),2,0))
 cb,cp=category(before),category(patch);delta=before.astype(np.float32)-patch.astype(np.float32);field=np.zeros_like(delta)
 for c in (0,1,2):
  valid=((cb==c)&(cp==c)).astype(np.float32);den=lowpass_field(valid)
  for channel in range(3):
   num=lowpass_field(delta[:,:,channel]*valid);v=num/np.maximum(den,0.001);field[:,:,channel][cp==c]=v[cp==c]
 distance=mask_distance(alpha>0)
 weight=np.maximum(0,1-distance/112.0)**2
 weight[alpha==0]=0
 field=np.clip(field,-32,32)*weight[:,:,None]
 adjusted=np.clip(np.rint(patch.astype(np.float32)+field),0,255).astype(np.uint8)
 fp=M/(label+'-local-color-field.npz');fp.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(fp,delta_rgb=field.astype(np.float16),weight=weight.astype(np.float16))
 return adjusted,dict(ref(fp),method='separate-material normalized low-frequency RGB difference field within insertion boundary only',fieldFilter='three separable 49px box passes on RGB DIFFERENCE only',maximumChannelDelta=32,innerFadeDistancePixels=112,distance='Manhattan to insertion-mask zero',fade='quadratic',artImageBlur=False,resampling=False,shapeWarp=False,changedPixels=int(np.any(adjusted!=patch,axis=2).sum()))

def lowpass_field(v):
 for _ in range(3):
  for axis in (0,1):
   pad=[(0,0),(0,0)];pad[axis]=(24,24);p=np.pad(v,pad,mode='reflect')
   c=np.cumsum(p,axis=axis,dtype=np.float64);z=np.take(c,[0],axis=axis)*0;c=np.concatenate((z,c),axis=axis)
   if axis==0:v=(c[49:]-c[:-49])/49
   else:v=(c[:,49:]-c[:,:-49])/49
 return v.astype(np.float32)

def mask_distance(mask):
 mask=np.pad(mask,1);h,w=mask.shape;xx=np.arange(w)[None,:]
 left=xx-np.maximum.accumulate(np.where(mask,-w,xx),axis=1)
 right=np.minimum.accumulate(np.where(mask,2*w,xx)[:,::-1],axis=1)[:,::-1]-xx
 d=np.minimum(left,right).astype(np.int32)
 for y in range(1,h):np.minimum(d[y],d[y-1]+1,out=d[y])
 for y in range(h-2,-1,-1):np.minimum(d[y],d[y+1]+1,out=d[y])
 return d[1:-1,1:-1]
def qa_extra(image):
 items=[];im=Image.fromarray(image)
 def add(name,box):
  box=[max(0,box[0]),max(0,box[1]),min(4096,box[2]),min(4096,box[3])]
  crop=im.crop(box)
  if max(crop.size)<=1536:
   info=save(Q/(name+'.png'),crop);pieces=None
  else:
   vertical=crop.height>1536;step=1024;length=crop.height if vertical else crop.width;n=(length+step-1)//step
   short=crop.width if vertical else crop.height
   sheet=Image.new('RGB',(short*n,step) if vertical else (step,short*n));pieces=[]
   for k in range(n):
    b=(0,k*step,short,min((k+1)*step,length)) if vertical else (k*step,0,min((k+1)*step,length),short)
    origin=(k*short,0) if vertical else (0,k*short)
    sheet.paste(crop.crop(b),origin);pieces.append({'cropRect':list(b),'sheetOrigin':list(origin)})
   info=save(Q/(name+'.png'),sheet)
  items.append(dict(info,sourceRectXYXY=box,nativePixelScale=1,resized=False,pieces=pieces,visualInspection='pending'))
 for y,n in [(472,'wood-h-top'),(1576,'wood-h-bottom')]:add(n,[0,y-128,4096,y+128])
 add('wood-h-left',[0,397,428,1651]);add('wood-h-right',[3668,397,4096,1651])
 for x,n in [(2520,'wood-r-left'),(3624,'wood-r-right')]:add(n,[x-160,1523,x+160,4057])
 add('wood-r-top',[2445,1491,3699,1811]);add('wood-r-bottom',[2445,3769,3699,4089])
 add('wood-r-overlap',[2445,2643,3699,2937])
 for name,box in [('water-a',[796,1956,1654,3229]),('water-b',[1396,2606,2304,3714]),('water-c',[796,2996,1264,4096]),('water-d',[1816,3476,2304,4096])]:add(name,box)
 return items
def build():
 assert sha(S)==BASE,'Source changed; cannot rebuild blindly.'
 base=rgb(S);assert base.shape==(4096,4096,3)
 oldmanifest=load(T/'output/assembly-manifest.json');assert oldmanifest['output']['sha256']==BASE
 sources=[];hpatch=[]
 for i,start in enumerate([0,1024,2048,2842],1):
  d=T/'repairs/wood-horizontal';p=d/f's{i}.png';arr,e=valid_patch(p);meta=load(d/f's{i}-input.png.generation.json');box=meta['sourceRectXYXY']
  assert box==[start,397,start+1254,1651] and raw(cut(base,box))==meta['rawSourceRGBSha256']
  expected=cut(base,box).copy()
  if i>1:
   ov=[0,1024,2048,2842][i-2]+1254-start;expected[:,:ov]=hpatch[-1][:,-ov:]
  assert np.array_equal(expected,rgb(d/f's{i}-input.png'))
  e.update(sourceROIValidated=True,sourceRectXYXY=box,rawSourceRGBSha256=meta['rawSourceRGBSha256']);hpatch.append(arr);sources.append(e)
 image=base.copy();horizontal=join(hpatch,[0,1024,2048,2842],'vertical',0,397,'wood-horizontal')
 insert(image,horizontal[:,128:3968],[128,397,3968,1651],500 if '--broad' in sys.argv else 150,'wood-horizontal')
 rpatch=[]
 for i,box in enumerate([[2445,1651,3699,2905],[2445,2675,3699,3929]],1):
  d=T/'repairs/wood-right';arr,e=valid_patch(d/f'w{i}.png');meta=load(d/f'w{i}-baseline.png.generation.json')
  assert raw(cut(base,box))==meta['rawRGBSha256'] and np.array_equal(cut(base,box),rgb(d/f'w{i}-baseline.png'))
  expected=cut(base,box).copy()
  if i>1:expected[:230]=rpatch[-1][-230:]
  assert np.array_equal(expected,rgb(d/f'w{i}-input.png'))
  e.update(sourceROIValidated=True,sourceRectXYXY=box,rawSourceRGBSha256=meta['rawRGBSha256']);rpatch.append(arr);sources.append(e)
 right=join(rpatch,[0,1024],'horizontal',2445,1651,'wood-right')
 insert(image,right,[2445,1651,3699,3929],500 if '--broad' in sys.argv else 150,'wood-right')
 for name in ['a-left-cross','b-right-cross','c-left-bottom','d-right-bottom']:
  d=T/'repairs/water-seams'/name;arr,e=valid_patch(d/'edited-native.png');meta=load(d/'input.png.generation.json');box=meta['sourceRectXYXY']
  assert raw(cut(base,box))==meta['rawSourceRGBSha256'] and np.array_equal(cut(base,box),rgb(d/'input.png'))
  maskmeta=load(d/'water-only-eligibility.json');assert sha(maskmeta['file'])==maskmeta['sha256'] and maskmeta['input']['sha256']==sha(d/'input.png')
  eligibility=np.asarray(Image.open(maskmeta['file']).convert('L'))
  e.update(sourceROIValidated=True,sourceRectXYXY=box,rawSourceRGBSha256=meta['rawSourceRGBSha256'],protectionMask=maskmeta)
  sources.append(e);insert(image,arr,box,64,'water-'+name,eligibility,meta['intendedRepairRectsXYXY'])
 if '--color' in sys.argv:
  for name,rects in [('e-hull-waterline',[[850,1880,1590,2250]]),('f-lantern-blueboard',[[1840,1800,2630,2300]])]:
   d=T/'repairs/water-seams'/name;arr,e=valid_patch(d/'edited-native.png');meta=load(d/'input.png.generation.json');box=meta['sourceRectXYXY']
   assert raw(cut(base,box))==meta['rawSourceRGBSha256'] and np.array_equal(cut(base,box),rgb(d/'input.png'))
   eligibility=None
   if name.startswith('f-'):
    original=cut(base,box).astype(np.int16);eligible=(original[:,:,2]>original[:,:,0]+25)&(original[:,:,1]>original[:,:,0]+10)
    eligibility=np.asarray(Image.fromarray(eligible.astype(np.uint8)*255).filter(ImageFilter.MinFilter(13)));save(M/'lantern-original-protection.png',Image.fromarray(eligibility))
   e.update(sourceROIValidated=True,sourceRectXYXY=box,rawSourceRGBSha256=meta['rawSourceRGBSha256']);sources.append(e);insert(image,arr,box,64,name,eligibility,rects)
 assert np.array_equal(image[GLOBAL_MASK==0],base[GLOBAL_MASK==0])
 assert np.array_equal(image[:,:128],base[:,:128]) and np.array_equal(image[:,-128:],base[:,-128:])
 candidate=save(C,Image.fromarray(image));oldex=T/'output/extended-context.png';assert sha(oldex)==oldmanifest['extendedContext']['sha256']
 extended=rgb(oldex);assert np.array_equal(extended[115:4211,115:4211],base);extended[115:4211,115:4211]=image
 exinfo=save(EX,Image.fromarray(extended));globalmask=save(M/'all-insertions-alpha-union.png',Image.fromarray(GLOBAL_MASK))
 a.QA=Q/'assembly';west,westinfo=a.checked_west();qa=a.write_qa(Image.fromarray(image),Image.fromarray(extended),west);extra=qa_extra(image)
 manifest={'createdAtUtc':a.utc_now(),'baseline':dict(ref(S),record=ref(T/'output/assembly-manifest.json')),'candidate':candidate,'extendedContext':exinfo,'nativeRepairs':sources,'seams':SEAMS,'insertions':INSERTIONS,'unionMask':globalmask,'outsideAuthorizedMaskChangedPixels':0,'westAndEast128ColumnsExactlyPreserved':True,'resampling':False,'imageBlur':False,'colorCorrection':'bounded local insertion-edge RGB field, material separated' if '--color' in sys.argv else False,'maskBlur':False,'maximumTransitionPixels':2,'formalAccepted':False,'wholeCityComplete':False,'qa':qa,'insertionQA':extra,'visualReview':'pending'}
 js(D/'manifest.json',manifest);print(json.dumps({'candidate':candidate,'qa':str(Q),'insertionQA':len(extra),'nativeRepairSources':len(sources)}))
def commit():
 m=load(D/'manifest.json');review=load(D/'review.json');assert review['candidateSha256']==sha(C) and review['result']=='pass'
 assert sha(S)==BASE and sha(C)==m['candidate']['sha256'] and sha(EX)==m['extendedContext']['sha256']
 oldpath=T/'output/assembly-manifest.json';old=load(oldpath);historical=D/'previous-assembly-manifest.json';shutil.copyfile(oldpath,historical)
 prior=dict(old['output'],availability='superseded',historicalRecord=ref(historical),pixelValidation='historical-record-and-validated-ROI-only')
 shutil.copyfile(C,S);shutil.copyfile(EX,T/'output/extended-context.png')
 newinfo={'file':str(S),'sha256':sha(S),'pixels':[4096,4096]};exinfo={'file':str(T/'output/extended-context.png'),'sha256':sha(T/'output/extended-context.png'),'pixels':[4326,4326]}
 old.update(output=newinfo,extendedContext=exinfo,status='complete-pixel-candidate-repaired-pending-independent-review',postprocessingProtected=True)
 old.setdefault('postprocessingChain',[]).append({'operation':'native material and water seam repairs without resampling','priorOutput':prior,'integrationManifest':ref(D/'manifest.json'),'review':ref(D/'review.json'),'output':newinfo,'extendedContext':exinfo})
 old['qa']=m['qa'];old['qaCoverage']['inspectionStatus']='internal-and-insertion-reviewed-independent-corners-west-pending'
 js(oldpath,old);js(Path(str(S)+'.generation.json'),dict(newinfo,operation='native patch assembly with recorded material/water seam postprocessing',assemblyManifest=ref(oldpath),postprocessingChain=old['postprocessingChain'],actualModel=None,actualQuality=None,formalAccepted=False))
 print(json.dumps({'committed':newinfo,'extendedContext':exinfo,'manifest':str(oldpath)}))

FN=a.load_seam_function();SEAMS=[];INSERTIONS=[];GLOBAL_MASK=np.zeros((4096,4096),np.uint8);joint.MASKS=M
if __name__=='__main__':
 if '--commit' in sys.argv:commit()
 else:build()

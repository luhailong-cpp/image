"""Single-writer integration of r07_c15 native repair sources; writes candidate only."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageFilter
import assembly_r07_c15 as a
from precolor_r07_c15 import lowpass,category
R=Path(__file__).resolve().parent;T=R/'r07_c15';D=T/'repairs/unified'
BASE=T/'output/r07_c15.png';BASE_SHA='3d6784d05e08447095081e0a2c425a1d11b2f7c461a7ff1dd74d9efa7644ea13'
SOUTH=R/'r08_c15/output/r08_c15.png';SOUTH_SHA='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
SEX=R/'r08_c15/output/extended-context.png';SEX_SHA='1824c937740587c2d7fa029c43ebfe15df4380ce9d15ad204924cbbe60572c72'
M=D/'masks';Q=D/'qa';C=D/'candidate.png';EX=D/'extended-context.png'
FN=a.load_seam_function();SEAMS=[];INSERTIONS=[];SOURCES=[];GLOBAL=np.zeros((4096,4096),np.uint8)
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def raw(x):return hashlib.sha256(x.tobytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':a.sha(p)}
def cut(x,b):return x[b[1]:b[3],b[0]:b[2]]
def seam(left,right,orient,box,label,protect_last=0):
 l=left if orient=='vertical' else left.transpose(1,0,2)
 r=right if orient=='vertical' else right.transpose(1,0,2)
 assert l.shape==r.shape
 w=l.shape[1];path=FN(l[:,:w-protect_last],r[:,:w-protect_last]) if protect_last else FN(l,r)
 alpha=a.seam_alpha(path,width=w)
 mixed=a.blend(l,r,alpha)
 mask=alpha if orient=='vertical' else alpha.T
 out=mixed if orient=='vertical' else mixed.transpose(1,0,2)
 p=a.writable(M/(label+'.npz'));np.savez_compressed(p,alpha_u8=mask,seam_offsets=path,rect_xyxy=np.asarray(box))
 SEAMS.append({'id':label,'orientation':orient,'rectXYXY':box,'mask':ref(p),'transitionPixels':2,'protectedLastPixels':protect_last})
 return out,mask
def color_field(before,patch):
 cb,cp=category(before),category(patch);delta=before.astype(np.float32)-patch.astype(np.float32)
 den=np.zeros(delta.shape[:2],np.float32);num=np.zeros_like(delta)
 for c in (0,1,2):
  valid=((cb==c)&(cp==c)).astype(np.float32);den+=lowpass(valid)
  for k in range(3):num[:,:,k]+=lowpass(delta[:,:,k]*valid)
 return np.clip(num/np.maximum(den[:,:,None],0.001),-32,32)
def distance(mask):
 h,w=mask.shape;xx=np.arange(w)[None,:]
 left=xx-np.maximum.accumulate(np.where(mask,-w,xx),axis=1)
 right=np.minimum.accumulate(np.where(mask,2*w,xx)[:,::-1],axis=1)[:,::-1]-xx
 d=np.minimum(left,right).astype(np.int32)
 for y in range(1,h):np.minimum(d[y],d[y-1]+1,out=d[y])
 for y in range(h-2,-1,-1):np.minimum(d[y],d[y+1]+1,out=d[y])
 return d
def match_color(before,patch,alpha,label):
 field=color_field(before,patch);weight=np.maximum(0,1-distance(alpha>0)/112.0)**2;weight[alpha==0]=0
 field*=weight[:,:,None]
 result=np.clip(np.rint(patch.astype(np.float32)+field),0,255).astype(np.uint8)
 p=a.writable(M/(label+'-color.npz'));np.savez_compressed(p,delta_rgb_f16=field.astype(np.float16),weight_f16=weight.astype(np.float16))
 return result,{'field':ref(p),'cap':32,'method':'Continuous material-agreement-normalized low-frequency RGB difference; three 49px passes on difference only; quadratic fade within112px of insertion zero; no art blur.'}
def join(patches,starts,y,label):
 out=patches[0].copy()
 for i,p in enumerate(patches[1:],1):
  ov=out.shape[1]-starts[i];l=out[:,-ov:];r=p[:,:ov]
  mix,alpha=seam(l,r,'vertical',[starts[i],y,starts[i]+ov,y+out.shape[0]],f'{label}-{i}')
  adjusted,cm=match_color(l,r,alpha,f'{label}-{i}');mix=a.blend(l,adjusted,alpha);SEAMS[-1]['colorMatch']=cm
  out=np.concatenate([out[:,:-ov],mix,p[:,ov:]],axis=1)
 return out
def valid_patch(folder,name):
 p=folder/'edited-native.png';record=Path(str(p)+'.generation.json');v=a.load_json(record)
 assert a.sha(p)==v['sha256'] and [v['width'],v['height']]==[1254,1254] and v['route']=='builtin'
 assert v['actualModel'] is None and v['actualQuality'] is None
 assert v['submittedParameters']['model'] is None and v['submittedParameters']['quality'] is None
 assert v['resizedAfterGeneration'] is False and v['finalArtUpscaled'] is False
 assert a.sha(v['prompt'])==v['promptSha256'] and v['evidence']['toolResultSha256']==a.sha(p)
 for e in v['references']:assert a.sha(e['file'])==e['sha256']
 ip=folder/'input.png';meta=a.load_json(str(ip)+'.generation.json');assert a.sha(ip)==meta['sha256']
 SOURCES.append({'id':name,**ref(p),'record':ref(record),'input':ref(ip),'inputRecord':ref(str(ip)+'.generation.json'),'sourceRectXYXY':v['sourceRectXYXY'],'actualModel':None,'actualQuality':None})
 return rgb(p),meta
def insert(image,patch,box,edge,label,eligibility=None,boundary_full=()):
 before=cut(image,box).copy();h,w=before.shape[:2];assert patch.shape==before.shape
 alpha=np.full((h,w),255,np.uint8);x0,y0,x1,y1=box;e=min(edge,(h-1)//2,(w-1)//2)
 for side in ('left','right','top','bottom'):
  if side in boundary_full:continue
  if side=='left':
   _,m=seam(before[:,:e],patch[:,:e],'vertical',[x0,y0,x0+e,y1],label+'-left');alpha[:,:e]=np.minimum(alpha[:,:e],m)
  elif side=='right':
   _,m=seam(patch[:,-e:],before[:,-e:],'vertical',[x1-e,y0,x1,y1],label+'-right');alpha[:,-e:]=np.minimum(alpha[:,-e:],255-m)
  elif side=='top':
   _,m=seam(before[:e],patch[:e],'horizontal',[x0,y0,x1,y0+e],label+'-top');alpha[:e]=np.minimum(alpha[:e],m)
  else:
   _,m=seam(patch[-e:],before[-e:],'horizontal',[x0,y1-e,x1,y1],label+'-bottom');alpha[-e:]=np.minimum(alpha[-e:],255-m)
 if eligibility is not None:alpha[~eligibility]=0
 adjusted,cm=match_color(before,patch,alpha,label)
 after=a.blend(before,adjusted,alpha);image[y0:y1,x0:x1]=after
 GLOBAL[y0:y1,x0:x1]=np.maximum(GLOBAL[y0:y1,x0:x1],alpha)
 assert np.array_equal(after[alpha==0],before[alpha==0])
 p=a.save_image(M/(label+'-insertion.png'),Image.fromarray(alpha))
 INSERTIONS.append({'id':label,'rectXYXY':box,'alpha':p,'colorMatch':cm,'originalAtZeroUnchanged':True,'boundaryFull':list(boundary_full)})
def extra_qa(image,south):
 im=Image.fromarray(image);items=[]
 def band(name,y):
  crop=im.crop((0,y-100,4096,y+100));sheet=Image.new('RGB',(1024,800))
  for k in range(4):sheet.paste(crop.crop((k*1024,0,(k+1)*1024,200)),(0,k*200))
  items.append({**a.save_image(Q/(name+'.png'),sheet),'sourceRectXYXY':[0,y-100,4096,y+100],'scale':1,'pieces':'four 1024x200 source segments stacked top-to-bottom','visualReview':'pending'})
 for label,y in [('h-insert-top',1720),('h-insert-bottom',2390),('south-insert-top',3469),('actual-halo-insert-top',3981)]:band(label,y)
 for i,x in enumerate([0,1024,2048,2842],1):
  p=Image.new('RGB',(1254,512));p.paste(im.crop((x,3840,x+1254,4096)),(0,0));p.paste(Image.fromarray(south[:256,x:x+1254]),(0,256))
  items.append({**a.save_image(Q/f'south-joint-{i}.png',p),'sourceRectXYXY':[x,3840,x+1254,4352],'scale':1,'visualReview':'pending'})
 items.append({**a.save_image(Q/'panel-insert.png',im.crop((0,2790,1190,3469))),'sourceRectXYXY':[0,2790,1190,3469],'scale':1,'visualReview':'pending'})
 return items
def main():
 assert a.sha(BASE)==BASE_SHA and a.sha(SOUTH)==SOUTH_SHA and a.sha(SEX)==SEX_SHA
 base=rgb(BASE);south=rgb(SOUTH);sex=rgb(SEX)
 assert np.array_equal(sex[115:4211,115:4211],south)
 pre=D/'precolor';pm=a.load_json(pre/'manifest.json');assert pm['baseline']['sha256']==BASE_SHA
 assert a.sha(pre/'candidate.png')==pm['candidate']['sha256']
 image=rgb(pre/'candidate.png');assert image.shape==base.shape
 starts=[0,1024,2048,2842];h=[]
 for i,x in enumerate(starts,1):
  p,meta=valid_patch(T/'repairs/native-seams'/f'h{i}',f'h{i}')
  box=[x,1421,x+1254,2675];assert raw(cut(base,box))==meta['rawUnmodifiedCropRGBSha256']
  h.append(p)
 fullh=join(h,starts,1421,'horizontal-repairs')
 insert(image,fullh[299:969],[0,1720,4096,2390],150,'horizontal-repairs',boundary_full=('left','right'))
 panel,meta=valid_patch(T/'repairs/native-seams/panel','panel')
 assert raw(cut(base,[0,2600,1254,3854]))==meta['rawUnmodifiedCropRGBSha256']
 region=cut(base,[0,2890,1040,3469]).astype(np.int16)
 eligible=(region[:,:,2]>region[:,:,0]+25)&(region[:,:,1]>region[:,:,0]+5)
 eligible=np.asarray(Image.fromarray(eligible.astype(np.uint8)*255).filter(ImageFilter.MinFilter(7)))>0
 insert(image,panel[290:869,:1040],[0,2890,1040,3469],70,'panel',eligible,('left',))
 s=[]
 for i,x in enumerate(starts,1):
  p,meta=valid_patch(D/'south-finishing'/f's{i}',f'south-finish-s{i}')
  assert meta['sourceRectXYXY']==[x,3469,x+1254,4723] and meta['south']['sha256']==SOUTH_SHA
  assert raw(rgb(D/'south-finishing'/f's{i}'/'input.png'))==meta['rawRGBSha256']
  s.append(p)
 fulls=join(s,starts,3469,'south-repairs')
 halo=sex[:115,115:4211]
 mixed,alpha=seam(fulls[512:627],halo,'horizontal',[0,3981,4096,4096],'south-existing-halo',protect_last=24)
 upper=np.concatenate([fulls[:512],mixed],axis=0)
 insert(image,upper,[0,3469,4096,4096],150,'south-repairs',boundary_full=('left','right','bottom'))
 # Last24 rows must be exact, authoritative north halo of fixed south.
 assert np.array_equal(image[-24:],halo[-24:])
 assert a.sha(SOUTH)==SOUTH_SHA and a.sha(SEX)==SEX_SHA
 union=GLOBAL>0
 with np.load(pre/'fields/final-correction.npz') as f:union |= np.any(f['correction_rgb_i16'][115:4211,115:4211]!=0,axis=2)
 assert np.array_equal(image[~union],base[~union])
 ex=rgb(T/'output/extended-context.png');assert np.array_equal(ex[115:4211,115:4211],base)
 ex[115:4211,115:4211]=image;ex[4211:,115:4211]=south[:115]
 ci=a.save_image(C,Image.fromarray(image));ei=a.save_image(EX,Image.fromarray(ex))
 a.ART=C;a.QA=Q/'assembly';qa=a.write_qa(Image.fromarray(image),Image.fromarray(ex),Image.fromarray(south))
 extras=extra_qa(image,south)
 mask=a.save_image(M/'all-changes-allowed.png',Image.fromarray(union.astype(np.uint8)*255))
 manifest={'createdAtUtc':a.utc_now(),'baseline':ref(BASE),'candidate':ci,'extendedContext':ei,'south':ref(SOUTH),'southExtended':ref(SEX),
 'precolor':ref(pre/'manifest.json'),'nativeRepairs':SOURCES,'seams':SEAMS,'insertions':INSERTIONS,'allowedMask':mask,
 'outsideAllowedMaskUnchanged':True,'southSourceUnchanged':True,'last24RowsEqualActualSouthNorthHalo':True,
 'sourcePixelsResampled':False,'registrationApplied':False,'imageBlur':False,'colorCorrection':'bounded local RGB difference fields <=32 per operation; difference-only filtering',
 'qa':qa,'insertionQA':extras,'visualReview':'pending','formalAccepted':False,'wholeCityComplete':False,
 'script':ref(__file__)}
 a.save_json(D/'manifest.json',manifest)
 print(json.dumps({'candidate':ci,'nativeSources':len(SOURCES),'qa':str(Q),'southUnchanged':True},indent=2))
if __name__=='__main__':main()


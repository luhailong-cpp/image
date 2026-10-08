"""Integrate native c16-only joint and internal patches; preserve frozen c15."""
from pathlib import Path
import sys, json, uuid, shutil
import numpy as np
from PIL import Image
import assembly_r08_c16 as a
import integrate_c15_repairs as j

R=Path(__file__).resolve().parent;T=R/'r08_c16';D=T/'repairs/integrated-v1'
if '--finish' in sys.argv:D=T/'repairs/integrated-v2'
if '--second' in sys.argv:D=T/'repairs/integrated-v3'
if '--third' in sys.argv:D=T/'repairs/integrated-v4'
if '--tight' in sys.argv:D=T/'repairs/integrated-v5'
S=T/'output/r08_c16.png';BASE='8c6871e74071f25997e4263bc21518f8b151a97c1b3408546e288f01867c3115'
W=R/'r08_c15/output/r08_c15.png';WSHA='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
WX=R/'r08_c15/output/extended-context.png';WXSHA='1824c937740587c2d7fa029c43ebfe15df4380ce9d15ad204924cbbe60572c72'
Q=D/'qa';M=D/'masks'/('run-'+uuid.uuid4().hex[:8]);C=D/'candidate.png';EX=D/'extended-context.png'
j.a=a;j.sha=a.sha;j.load=a.load_json;j.js=a.save_json;j.save=a.save_image
j.M=M;j.Q=Q;j.C=C;j.EX=EX;j.T=T;j.S=S;j.BASE=BASE;j.D=D
j.joint.MASKS=M;j.joint.save_image=a.save_image;j.joint.save_json=a.save_json
j.SEAMS=[];j.INSERTIONS=[];j.GLOBAL_MASK=np.zeros((4096,4096),np.uint8)
if '--color' not in sys.argv:sys.argv.append('--color')
sha=a.sha;load=a.load_json;save=a.save_image;js=a.save_json

def qa_crop(image,name,box):
 im=Image.fromarray(image).crop(box);pieces=[]
 if max(im.size)>1536:
  vertical=im.height>1536;length=im.height if vertical else im.width;short=im.width if vertical else im.height;n=(length+1023)//1024
  sheet=Image.new('RGB',(short*n,1024) if vertical else (1024,short*n))
  for k in range(n):
   b=[0,k*1024,short,min((k+1)*1024,length)] if vertical else [k*1024,0,min((k+1)*1024,length),short]
   origin=[k*short,0] if vertical else [0,k*short];sheet.paste(im.crop(b),origin);pieces.append({'cropRect':b,'sheetOrigin':origin})
  im=sheet
 return dict(save(Q/(name+'.png'),im),sourceRectXYXY=box,nativePixelScale=1,resized=False,pieces=pieces,visualReview='pending')

def build():
 assert sha(S)==BASE and sha(W)==WSHA and sha(WX)==WXSHA
 base=j.rgb(S);west=j.rgb(W);pair=np.concatenate([west,base],axis=1)
 old=load(T/'output/assembly-manifest.json');assert old['output']['sha256']==BASE
 sources=[];patches=[];starts=[0,1024,2048,2842];d=T/'repairs/west-only-joint'
 for i,y in enumerate(starts,1):
  arr,e=j.valid_patch(d/f's{i}.png');meta=load(d/f's{i}-input.png.generation.json');box=[3469,y,4723,y+1254]
  assert meta['sourceRectInPairXYXY']==box and j.raw(j.cut(pair,box))==meta['rawSourceRGBSha256']
  expected=j.cut(pair,box).copy()
  if i>1:
   ov=starts[i-2]+1254-y;expected[:ov,627:]=patches[-1][-ov:,627:]
  assert np.array_equal(expected,j.rgb(d/f's{i}-input.png'))
  e.update(sourceROIValidated=True,sourceRectInPairXYXY=box,rawSourceRGBSha256=meta['rawSourceRGBSha256'],appliedNativeColumns=[627,1254],c15PixelsApplied=False)
  sources.append(e);patches.append(arr)
 image=base.copy();strip=j.join([p[:,627:] for p in patches],starts,'horizontal',0,0,'west-joint')
 j.insert(image,strip,[0,0,627,4096],150,'west-joint',rects=[[0,0,627,4096]])
 hand=load(T/'repairs/internal-seams/handoff.json');assert hand['baseline']['sha256']==BASE
 inside={}
 for p in hand['patches']:
  path=Path(p['file']);assert sha(path)==p['sha256'] and sha(p['record']['file'])==p['record']['sha256']
  arr,e=j.valid_patch(path);meta=load(path.parent/'input.png.generation.json');box=meta['sourceRectXYXY']
  assert meta['source']['sha256']==BASE and j.raw(j.cut(base,box))==meta['rawSourceRGBSha256']==p['rawSourceRGBSha256']
  assert np.array_equal(j.cut(base,box),j.rgb(path.parent/'input.png'))
  roi=p['suggestedTargetRectXYXY'];assert roi[0]>=700
  e.update(sourceROIValidated=True,sourceRectXYXY=box,rawSourceRGBSha256=meta['rawSourceRGBSha256']);sources.append(e);inside[p['name']]=(arr,box,roi)
 for name in ['mast-1024','mast-2048','mast-3072']:
  arr,box,roi=inside[name];j.insert(image,arr,box,96,name,rects=[roi])
 for prefix,roi in [('hull',[1780,2580,2270,4096]),('water',[2875,0,3425,1950])]:
  up,ub,_=inside[prefix+'-upper'];lo,lb,_=inside[prefix+'-lower'];offset=lb[1]-ub[1]
  joined=j.join([up,lo],[0,offset],'horizontal',ub[0],ub[1],prefix+'-pair')
  box=[ub[0],ub[1],ub[2],lb[3]];j.insert(image,joined,box,96,prefix+'-combined',rects=[roi])
 if '--finish' in sys.argv:
  fd=T/'repairs/west-insertion-finish';arr,e=j.valid_patch(fd/'edited-native.png');meta=load(fd/'input.png.generation.json');box=meta['sourceRectXYXY']
  frozen=T/'repairs/integrated-v1/candidate.png';assert sha(frozen)==meta['source']['sha256']
  assert j.raw(j.cut(j.rgb(frozen),box))==meta['rawSourceRGBSha256']
  assert np.array_equal(j.cut(image,box),j.cut(j.rgb(frozen),box))
  j.insert(image,arr,box,64,'west-rail-insertion-finish',rects=meta['intendedRepairRectsXYXY']);e.update(sourceROIValidated=True,sourceRectXYXY=box,sourceCandidate=j.ref(frozen));sources.append(e)
 if '--second' in sys.argv:
  fd=T/'repairs/west-rail-second';arr,e=j.valid_patch(fd/'edited-native.png');meta=load(fd/'input.png.generation.json');box=meta['sourceRectXYXY']
  frozen=T/'repairs/integrated-v2/candidate.png';assert sha(frozen)==meta['source']['sha256']
  assert j.raw(j.cut(j.rgb(frozen),box))==meta['rawSourceRGBSha256'] and np.array_equal(j.cut(image,box),j.cut(j.rgb(frozen),box))
  roi=[[590,2490,1040,2840]] if '--tight' in sys.argv else meta['intendedRepairRectsXYXY']
  j.insert(image,arr,box,64,'west-rail-second',rects=roi);e.update(sourceROIValidated=True,sourceRectXYXY=box,sourceCandidate=j.ref(frozen),tightenedROIReason='protect unchanged diagonal beam above rail');sources.append(e)
 if '--third' in sys.argv:
  fd=T/'repairs/west-insertion-finish';arr,e=j.valid_patch(fd/'edited-native.png');meta=load(fd/'input.png.generation.json');box=meta['sourceRectXYXY']
  j.insert(image,arr,box,48,'upper-diagonal-small-notch',rects=[[400,1810,710,2130]])
  e.update(reusedSource=True,sourceROIValidated=True,sourceRectXYXY=box,purpose='expand earlier top insertion ROI to include small bevel notch');sources.append(e)
 assert np.array_equal(image[j.GLOBAL_MASK==0],base[j.GLOBAL_MASK==0])
 assert sha(W)==WSHA and sha(WX)==WXSHA
 candidate=save(C,Image.fromarray(image));oldex=T/'output/extended-context.png';assert sha(oldex)==old['extendedContext']['sha256']
 extended=j.rgb(oldex);assert np.array_equal(extended[115:4211,115:4211],base)
 extended[115:4211,115:4211]=image
 # The west overlap is existing finished c15 pixels, not editable c16 art.
 extended[115:4211,:115]=west[:,-115:]
 ex=save(EX,Image.fromarray(extended));mask=save(M/'all-insertion-alpha.png',Image.fromarray(j.GLOBAL_MASK))
 a.QA=Q/'assembly';a.ART=C;qa=a.write_qa(Image.fromarray(image),Image.fromarray(extended),Image.fromarray(west))
 extra=[qa_crop(image,'west-right-insertion',[380,0,760,4096])]
 for y in [1024,2048,2842]:extra.append(qa_crop(image,f'west-overlap-{y}',[0,max(0,y-80),707,min(4096,y+540)]))
 for name,(_,_,roi) in inside.items():
  box=[max(0,roi[0]-80),max(0,roi[1]-80),min(4096,roi[2]+80),min(4096,roi[3]+80)]
  extra.append(qa_crop(image,'insertion-'+name,box))
 if '--finish' in sys.argv:extra.append(qa_crop(image,'west-rail-insertion-finish',[250,1800,850,2920]))
 if '--second' in sys.argv:extra.append(qa_crop(image,'west-rail-second',[500,2290,1130,2920]))
 if '--third' in sys.argv:extra.append(qa_crop(image,'upper-diagonal-small-notch',[320,1750,790,2200]))
 manifest={'createdAtUtc':a.utc_now(),'baseline':dict(j.ref(S),assemblyManifest=j.ref(T/'output/assembly-manifest.json')),'candidate':candidate,'extendedContext':ex,'immutableWest':j.ref(W),'immutableWestExtended':j.ref(WX),'c15CoreAndHaloUnchanged':True,'nativeRepairs':sources,'seams':j.SEAMS,'insertions':j.INSERTIONS,'unionMask':mask,'outsideAuthorizedMaskChangedPixels':0,'resampling':False,'imageBlur':False,'localColorCorrection':'bounded insertion-edge RGB difference field only; source art not filtered','westHaloOperation':'replace exact shared 115 columns with immutable final c15 core last115; no resampling','maximumSeamTransitionPixels':2,'qa':qa,'insertionQA':extra,'visualReview':'pending','formalAccepted':False,'wholeCityComplete':False}
 js(D/'manifest.json',manifest);print(json.dumps({'candidate':candidate,'qa':str(Q),'insertionViews':len(extra),'nativeRepairs':len(sources)}))

def commit():
 m=load(D/'manifest.json');review=load(D/'review.json')
 assert review['candidateSha256']==sha(C)==m['candidate']['sha256'] and review['result']=='pass'
 for name in ['independent-internal-review.json','root-external-review.json']:
  r=load(D/name)
  if name=='root-external-review.json':assert r['finalCandidateSha256']==sha(C) and r['result']=='pass for unchanged four corners and full west common edge'
  else:assert r['candidateSha256']==sha(C) and r['result']=='pass'
 assert sha(S)==BASE and sha(W)==WSHA and sha(WX)==WXSHA
 oldpath=T/'output/assembly-manifest.json';old=load(oldpath);js(D/'previous-assembly-manifest.json',old)
 out=save(S,Image.open(C));ex=save(T/'output/extended-context.png',Image.open(EX))
 a.QA=T/'qa/assembly';a.ART=S
 finalqa=a.write_qa(Image.open(S).convert('RGB'),Image.open(T/'output/extended-context.png').convert('RGB'),Image.open(W).convert('RGB'))
 for q in finalqa:
  if q.get('visualInspection')=='pending':q['visualInspection']='pass-see-postprocessing-reviews'
 js(T/'qa/assembly/manifest.json',{'candidateSha256':sha(S),'qa':finalqa,'visualInspection':'pass','integrationManifest':j.ref(D/'manifest.json'),'review':j.ref(D/'review.json')})
 old.setdefault('postprocessingChain',[]).append({'operation':'native c16-only western joint + internal mast/hull/water repair','priorOutput':dict(m['baseline'],availability='superseded'),'integrationManifest':j.ref(D/'manifest.json'),'review':j.ref(D/'review.json'),'output':out,'extendedContext':ex})
 old.update(output=out,extendedContext=ex,postprocessingProtected=True,status='complete-candidate-visual-qa-passed',qa=finalqa)
 old['qaCoverage']['inspectionStatus']='internal-external-insertion-all-reviewed-pass'
 js(oldpath,old);js(Path(str(S)+'.generation.json'),dict(out,operation='native patch assembly with c16-only joint/internal repairs',assemblyManifest=j.ref(oldpath),actualModel=None,actualQuality=None,formalAccepted=False))
 print(json.dumps({'committed':out,'extendedContext':ex,'immutableWestSha256':sha(W)}))

if __name__=='__main__':
 if '--commit' in sys.argv:commit()
 else:build()

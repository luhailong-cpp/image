"""Refine only r07_c15 south repair using masked native edits and registered existing outlines."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import integrate_r07_c15 as i
a=i.a;R=Path(__file__).resolve().parent;D=R/'r07_c15/repairs/unified';F=D/'south-masked';O=D/'refined'
BASE=D/'candidate.png';EXPECTED='0a677ad6deb2347659789f3c45a5055b1611ea0cffeff0d5a6e64c40e7df6a52'
def main():
 assert a.sha(BASE)==EXPECTED and a.sha(i.SOUTH)==i.SOUTH_SHA and a.sha(i.SEX)==i.SEX_SHA
 i.M=O/'masks';i.Q=O/'qa';i.SEAMS.clear();i.INSERTIONS.clear();i.SOURCES.clear();i.GLOBAL[:]=0
 im=i.rgb(BASE);before=im.copy();patches=[];regs=[]
 for n,x in zip(['s1','s2','s3','s4'],[0,1024,2048,2842]):
  f=F/n;p,m=i.valid_patch(f,'masked-'+n)
  for r in m['sources']:assert a.sha(r['file'])==r['sha256']
  assert m['sourceRectXYXY']==[x,3300,x+1254,4554]
  h=f/'halo-matched-upper.png';up=i.rgb(h);assert up.shape==(796,1254,3)
  assert np.array_equal(up[-1],i.rgb(i.SEX)[114,115+x:115+x+1254])
  patches.append(up[350:796])
  regs.append({'id':n,'registeredPatch':i.ref(h),'registrationRecord':i.ref(f/'semantic-registration.json'),'coordinateMap':i.ref(f/'semantic-registration.npz')})
 joined=i.join(patches,[0,1024,2048,2842],3650,'masked-south')
 joined[-1]=i.rgb(i.SEX)[114,115:4211]
 # Known last row is identical in all overlapping patches and therefore remains exact.
 i.insert(im,joined,[0,3650,4096,4096],80,'masked-south',boundary_full=('left','right','bottom'))
 # Restore the real dark wall above the rectangular south insertion, using the same existing-material mask.
 darkup=i.rgb(F/'s1'/'halo-matched-upper.png')
 with np.load(F/'s1'/'existing-dark-wall-mask.npz') as z:wall=z['alpha_f16'].astype(np.float32)
 im[3300:4096,:1254]=np.rint(im[3300:4096,:1254]*(1-wall[:,:,None])+darkup*wall[:,:,None]).astype(np.uint8)
 assert np.array_equal(im[:3300],before[:3300])
 sex=i.rgb(i.SEX);south=i.rgb(i.SOUTH);assert np.array_equal(im[-1],sex[114,115:4211])
 assert a.sha(i.SOUTH)==i.SOUTH_SHA and a.sha(i.SEX)==i.SEX_SHA
 ex=i.rgb(D/'extended-context.png');assert np.array_equal(ex[115:4211,115:4211],before)
 ex[115:4211,115:4211]=im
 ci=a.save_image(O/'candidate.png',Image.fromarray(im));ei=a.save_image(O/'extended-context.png',Image.fromarray(ex))
 a.ART=O/'candidate.png';a.QA=O/'qa/assembly';qa=a.write_qa(Image.fromarray(im),Image.fromarray(ex),Image.fromarray(south))
 extras=i.extra_qa(im,south)
 # Full crop at native pixels, four overlapped join segments.
 for j,x in enumerate([0,1024,2048,2842],1):
  sh=Image.new('RGB',(1254,896));sh.paste(Image.fromarray(im[3400:4096,x:x+1254]),(0,0));sh.paste(Image.fromarray(south[:200,x:x+1254]),(0,696));a.save_image(O/f'qa/full-south-{j}.png',sh)
 manifest={'createdAtUtc':a.utc_now(),'input':i.ref(BASE),'inputManifest':i.ref(D/'manifest.json'),'candidate':ci,'extendedContext':ei,'south':i.ref(i.SOUTH),'southExtended':i.ref(i.SEX),'nativeMaskedSources':i.SOURCES,'registrations':regs,'seams':i.SEAMS,'insertions':i.INSERTIONS,'outsideRectUnchanged':{'rect':[0,3300,4096,4096],'confirmed':True},'southUnchanged':True,'lastRowExactAuthoritativeHalo':True,'imageBlur':False,'localSourceResampling':'bilinear horizontal object-edge registration only; no art upscale','qa':qa,'insertionQA':extras,'script':i.ref(__file__),'visualReview':'pending','formalAccepted':False}
 a.save_json(O/'manifest.json',manifest);print(json.dumps(ci))
if __name__=='__main__':main()


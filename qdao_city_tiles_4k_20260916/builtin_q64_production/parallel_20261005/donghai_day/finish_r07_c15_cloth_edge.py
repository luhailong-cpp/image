"""Remove only last rope-shadow cut in blue material; protect actual warm rope."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image
import integrate_r07_c15 as i
import finish_r07_c15_candidate_v2 as f
a=i.a;D=i.D;P=D/'straight-integrated-v5';O=D/'straight-integrated-v6'

def main():
 assert a.sha(P/'candidate.png')=='c388382e2da8c67122ef05966aca91bc75f968ea0c1cf35c3d638cba2054cbee'
 im=i.rgb(P/'candidate.png');before=im.copy();b=[3722,3870,4096,4080]
 old=i.cut(i.rgb(D/'straight-integrated/candidate.png'),b).astype(np.float32)
 patch,rec=f.native(D/'south-straight/s4-cloth-edge')
 blue=(old[:,:,2]>old[:,:,0]+45)&(old[:,:,1]>old[:,:,0]+30)
 dist=f.cv2.distanceTransform(blue.astype(np.uint8),f.cv2.DIST_L2,5);x=np.arange(374)[None,:];y=np.arange(210)[:,None]
 radius=22-21*f.smooth((x-200)/75)
 al=f.smooth(dist/radius)*f.smooth(x/70)*f.smooth(y/45)*f.smooth((209-y)/45)
 # Reconstruct from the pre-cloth candidate so the unchanged side retains identical pixels.
 im[b[1]:b[3],b[0]:b[2]]=old.astype(np.uint8)
 f.O=O;i.INSERTIONS.clear();f.continuous_insert(im,patch[730:940,880:1254],b,al,'cloth-edge-full-right-blue')
 changed=np.any(im!=before,axis=2);ys,xs=np.where(changed);bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 assert np.array_equal(im[-1],before[-1]);assert np.array_equal(im[:3370],before[:3370])
 assert a.sha(i.SOUTH)==i.SOUTH_SHA and a.sha(i.SEX)==i.SEX_SHA
 ex=i.rgb(P/'extended-context.png');ex[115:4211,115:4211]=im;south=i.rgb(i.SOUTH)
 ci=a.save_image(O/'candidate.png',Image.fromarray(im));ei=a.save_image(O/'extended-context.png',Image.fromarray(ex))
 a.ART=O/'candidate.png';a.QA=O/'qa/assembly';qa=a.write_qa(Image.fromarray(im),Image.fromarray(ex),Image.fromarray(south));i.Q=O/'qa';extra=i.extra_qa(im,south)
 for j,x0 in enumerate([0,1024,2048,2842],1):a.save_image(O/f'qa/full-south-{j}.png',Image.fromarray(np.concatenate([im[3370:4096,x0:x0+1254],south[:200,x0:x0+1254]],axis=0)))
 a.save_image(O/'qa/cloth-edge.png',Image.fromarray(im[3820:4096,3672:4096]))
 a.save_image(O/'qa/cloth-right-tail.png',Image.fromarray(im[3900:4050,3950:4096]))
 proofs=[]
 for p in sorted((O/'qa/assembly').glob('*.png')):
  q=P/'qa/assembly'/p.name
  if a.sha(p)==a.sha(q):proofs.append({'name':p.name,'sha256':a.sha(p),'identicalToV5':True})
 a.save_json(O/'manifest.json',{'createdAtUtc':a.utc_now(),'input':i.ref(P/'candidate.png'),'inputManifest':i.ref(P/'manifest.json'),'candidate':ci,'extendedContext':ei,'south':i.ref(i.SOUTH),'southExtended':i.ref(i.SEX),'nativeSource':rec,'insertions':i.INSERTIONS,'changedBoundsXYXY':bounds,'changedPixels':int(changed.sum()),'outsideChangedBoundsExact':True,'warmRopePixelsPreserved':bool(np.array_equal(im[b[1]:b[3],b[0]:b[2]][~blue],before[b[1]:b[3],b[0]:b[2]][~blue])),'maskAdjustment':'Continuous transition of blue-only feather radius from22 to1px over local x200..275, full supported blue immediately below existing rope at right edge. Warm rope and wood excluded.','imageBlur':False,'spatialResampling':False,'lastRowExactAuthoritativeHalo':True,'southUnchanged':True,'unchangedQA':proofs,'qa':qa,'insertionQA':extra,'script':i.ref(__file__),'visualReview':'pending','formalAccepted':False})
 print(json.dumps({'candidate':ci,'changedBounds':bounds,'unchangedQA':len(proofs)}))
if __name__=='__main__':main()

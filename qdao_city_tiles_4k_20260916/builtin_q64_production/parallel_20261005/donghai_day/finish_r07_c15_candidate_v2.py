"""Add three strictly local native join repairs to frozen reviewed geometry."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import integrate_r07_c15 as i
a=i.a;D=i.D;P=D/'straight-integrated';O=D/'straight-integrated-v5';F=D/'south-straight'
import sys
sys.path.insert(0,str(D/'python-deps'))
import cv2

def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)

def continuous_insert(im,patch,b,alpha,label):
 old=i.cut(im,b).copy();field=i.color_field(old,patch)
 # Low frequency color difference only, continuous perimeter fade.
 weight=(1-alpha)**2*(alpha>0);adjusted=np.clip(np.rint(patch.astype(np.float32)+field*weight[:,:,None]),0,255)
 im[b[1]:b[3],b[0]:b[2]]=np.rint(old*(1-alpha[:,:,None])+adjusted*alpha[:,:,None]).astype(np.uint8)
 fp=a.writable(O/'masks'/(label+'-continuous.npz'));np.savez_compressed(fp,alpha_f16=alpha.astype(np.float16),color_delta_f16=(field*weight[:,:,None]).astype(np.float16),rect_xyxy=b)
 i.INSERTIONS.append({'id':label,'rectXYXY':b,'maskAndDifference':i.ref(fp),'colorCap':32,'artBlur':False,'method':'Continuous alpha source integration, smoothing weights/difference only, no spatial resampling'})

def native(folder):
 p=folder/'edited-native.png';rec=Path(str(p)+'.generation.json');r=a.load_json(rec)
 assert a.sha(p)==r['sha256']==r['evidence']['toolResultSha256']
 assert r['route']=='builtin' and r['actualModel'] is None and r['actualQuality'] is None
 assert r['resizedAfterGeneration'] is False and [r['width'],r['height']]==[1254,1254]
 assert a.sha(r['prompt'])==r['promptSha256']
 for f in r['references']:assert a.sha(f['file'])==f['sha256']
 return i.rgb(p),{'native':i.ref(p),'record':i.ref(rec)}

def main():
 assert a.sha(P/'candidate.png')=='4ae2d12b93561fe18b8f0b1b65290f4ff72ccec96d86b60adadf27e70a0f8411'
 assert a.sha(i.SOUTH)==i.SOUTH_SHA and a.sha(i.SEX)==i.SEX_SHA
 i.M=O/'masks';i.Q=O/'qa';i.SEAMS.clear();i.INSERTIONS.clear();i.GLOBAL[:]=0
 im=i.rgb(P/'candidate.png');before=im.copy();south=i.rgb(i.SOUTH);ex=i.rgb(P/'extended-context.png')
 bridge,br=native(F/'join-bridges')
 for name,b,edge in [('join-left',[970,3567,1250,4045],38)]:
  src=bridge[b[1]-2842:b[3]-2842,b[0]-920:b[2]-920]
  i.insert(im,src,b,edge,name)
 b=[1720,3392,2174,4045];x=np.arange(b[0],b[2])[None,:];y=np.arange(b[1],b[3])[:,None]
 d=y-(5715-x)
 al=smooth((x-1720)/210)*smooth((2174-x)/100)*smooth((d+85)/45)*smooth((22-d)/12)
 continuous_insert(im,bridge[b[1]-2842:b[3]-2842,b[0]-920:b[2]-920],b,al,'join-right-long-contour')
 cloth,cr=native(F/'s4-cloth-edge');b=[3722,3870,4096,4080];old=i.cut(im,b).astype(np.float32)
 blue=(old[:,:,2]>old[:,:,0]+45)&(old[:,:,1]>old[:,:,0]+30)
 dist=cv2.distanceTransform(blue.astype(np.uint8),cv2.DIST_L2,5);x=np.arange(374)[None,:];y=np.arange(210)[:,None]
 al=smooth(dist/22)*smooth(x/70)*smooth(y/45)*smooth((209-y)/45)
 continuous_insert(im,cloth[730:940,880:1254],b,al,'cloth-edge-continuous')
 assert np.array_equal(im,i.rgb(D/'straight-integrated-v4/candidate.png'))
 finalcontour,fr=native(F/'right-contour-final');b=[1890,3560,2270,3900]
 i.insert(im,finalcontour[b[1]-2842:b[3]-2842,b[0]-1420:b[2]-1420],b,60,'right-contour-final')
 assert np.array_equal(im[:3370],before[:3370])
 assert np.array_equal(im[-1],before[-1])
 assert np.array_equal(im[:3236,3469:],i.rgb(D/'refined/candidate.png')[:3236,3469:])
 assert i.raw(im[2970:3160,430:790])=='d7841848d833f7df52f2f1e8104b1400cfaa8d486d57798b0686b490f405d3a5'
 ex[115:4211,115:4211]=im
 ci=a.save_image(O/'candidate.png',Image.fromarray(im));ei=a.save_image(O/'extended-context.png',Image.fromarray(ex))
 a.ART=O/'candidate.png';a.QA=O/'qa/assembly';qa=a.write_qa(Image.fromarray(im),Image.fromarray(ex),Image.fromarray(south));extras=i.extra_qa(im,south)
 for j,x in enumerate([0,1024,2048,2842],1):
  p=np.concatenate([im[3370:4096,x:x+1254],south[:200,x:x+1254]],axis=0);a.save_image(O/f'qa/full-south-{j}.png',Image.fromarray(p))
 for name,b in [('left-bridge',[930,3527,1300,4080]),('right-bridge',[1920,3392,2224,3887]),('cloth-edge',[3672,3820,4096,4096]),('panel-contour-detail',[430,2970,790,3160])]:a.save_image(O/f'qa/{name}.png',Image.fromarray(i.cut(im,b)))
 proofs=[]
 for f in sorted((O/'qa/assembly').glob('*.png')):
  old=P/'qa/assembly'/f.name
  if old.exists() and a.sha(old)==a.sha(f):proofs.append({'name':f.name,'sha256':a.sha(f),'sameAsStraightIntegrated':True})
 a.save_json(O/'manifest.json',{'createdAtUtc':a.utc_now(),'input':i.ref(P/'candidate.png'),'inputManifest':i.ref(P/'manifest.json'),'candidate':ci,'extendedContext':ei,'south':i.ref(i.SOUTH),'southExtended':i.ref(i.SEX),'nativeSources':[br,cr,fr],'clothHandoff':i.ref(F/'s4-cloth-edge/handoff.json'),'seams':i.SEAMS,'insertions':i.INSERTIONS,'noSpatialResamplingThisStep':True,'imageBlur':False,'eastFullPixelProof':{'rect':[3469,0,4096,4096],'baseline':i.ref(D/'straight-integrated-v4/candidate.png'),'RGBSha256':i.raw(im[:,3469:]),'equal':np.array_equal(im[:,3469:],i.rgb(D/'straight-integrated-v4/candidate.png')[:,3469:])},'eastUpperPixelProof':{'rect':[3469,0,4096,3236],'baselineSha256':'965caba9070b2a41daa9b2c2b1e5ec1d292bfa3970965fe89d4f6ebb2ace3a40','RGBSha256':i.raw(im[:3236,3469:]),'equal':True},'panelProof':{'rect':[430,2970,790,3160],'rawRGBSha256':i.raw(im[2970:3160,430:790]),'review':i.ref(P/'independent-panel-review.json'),'equal':True},'unchangedQA':proofs,'southUnchanged':True,'lastRowExactAuthoritativeHalo':True,'qa':qa,'insertionQA':extras,'script':i.ref(__file__),'visualReview':'pending','formalAccepted':False})
 print(json.dumps({'candidate':ci,'unchangedQACount':len(proofs)}))
if __name__=='__main__':main()

"""Merge disjoint reviewed north and east repairs; candidate only, no canonical write."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
import assembly_r10_c15 as a
R=Path(__file__).resolve().parent;T=R/'r10_c15';D=T/'repairs/final-integrated';Q=D/'qa'
B=T/'repairs/north-integrated-v2/candidate.png';BS='56aa9499341914dbf11e50fe2d405e768c5874120ee873dc8a4763ae00db40a7'
E=T/'repairs/north-right-color-v3/candidate.png';ES='b03d748d0f13ef9760bf6f222f49b508347175b6249b73a16fbf91e53780b47b'
EH='7b748b6091d838a6b86bc4a7d65e5097d2bba90d6ffc413fc69f9b2e9dacafaa'
def rgb(p):
 with Image.open(p) as im:im.load();assert im.size==(4096,4096);return np.asarray(im.convert('RGB')).copy()
def raw(v):return hashlib.sha256(v.tobytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':a.sha(p)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--north',required=True);p.add_argument('--north-sha',required=True);p.add_argument('--north-manifest',required=True);args=p.parse_args()
 n=Path(args.north).resolve();nm=Path(args.north_manifest).resolve()
 assert n.is_relative_to((T/'repairs/north-joint').resolve()) and nm.is_relative_to((T/'repairs/north-joint').resolve())
 assert a.sha(B)==BS and a.sha(E)==ES and a.sha(n)==args.north_sha
 base=rgb(B);east=rgb(E);north=rgb(n);changes=np.any(base!=north,axis=2)
 assert not changes[700:].any() and not changes[:,3180:].any(),'North field violates frozen scope'
 final=east.copy();final[changes]=north[changes]
 assert np.array_equal(final[700:],east[700:]) and raw(final[700:,3469:])==EH and np.array_equal(final[:,3180:],east[:,3180:])
 out=a.save_image(D/'candidate.png',Image.fromarray(final))
 with Image.open(E.parent/'extended-context.png') as im:ext=np.asarray(im.convert('RGB')).copy()
 assert np.array_equal(ext[115:4211,115:4211],east);ext[115:4211,115:4211]=final
 ex=a.save_image(D/'extended-context.png',Image.fromarray(ext));mask=a.save_image(D/'masks/north-change-mask.png',Image.fromarray(changes.astype(np.uint8)*255))
 a.QA=Q/'assembly';a.ART=D/'candidate.png';neighbor,ni=a.checked_north();qa=a.write_qa(Image.fromarray(final),Image.fromarray(ext),neighbor)
 paired=np.concatenate([np.asarray(neighbor),final],axis=0);extra=[]
 for i,x in enumerate([0,1024,2048,2842],1):
  b=[x,3796,x+1254,4566];extra.append(dict(a.save_image(Q/f'north-wide-{i}.png',Image.fromarray(paired[b[1]:b[3],b[0]:b[2]])),sourceRectInNorthPair=b,resized=False))
 for name,b in [('north-left-insertion',[750,0,1110,707]),('north-middle-insertion',[1920,0,2250,707]),('north-right-insertion',[3090,0,3430,707]),('north-bottom-left',[800,450,2054,710]),('north-bottom-right',[2054,450,3308,710])]:
  extra.append(dict(a.save_image(Q/(name+'.png'),Image.fromarray(final[b[1]:b[3],b[0]:b[2]])),sourceRectXYXY=b,resized=False))
 identity=[]
 for item in qa:
  path=Path(item['file']);prior=E.parent/'qa/assembly'/path.name
  if prior.exists():identity.append({'file':str(path),'sha256':a.sha(path),'prior':str(prior),'priorSha256':a.sha(prior),'pixelIdentical':a.sha(path)==a.sha(prior)})
 a.save_json(D/'manifest.json',{'createdAtUtc':a.utc_now(),'candidate':out,'extendedContext':ex,'eastBase':ref(E),'northBase':ref(B),'northCandidate':ref(n),'northManifest':ref(nm),'northChangedPixels':int(changes.sum()),'northChangeMask':mask,'east627BelowY700RawRGBSha256':EH,'east627RawRGBSha256':raw(final[:,3469:]),'qa':qa,'insertionQA':extra,'pixelIdentityAgainstEastBase':identity,'outsideNorthChangeMaskPreserved':True,'nativeSourcesUnchanged':True,'imageResampling':False,'imageBlur':False,'formalAccepted':False,'visualReview':'pending'})
 print(json.dumps({'candidate':out,'qa':str(Q),'northChangedPixels':int(changes.sum()),'east627BelowY700RawRGBSha256':EH,'east627RawRGBSha256':raw(final[:,3469:])}))
if __name__=='__main__':main()


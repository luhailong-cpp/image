"""Bounded RGB difference field on the reviewed west border; no geometry editing."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
import assembly_r10_c16 as a
from qa_r10_pair import probes
R=Path(__file__).resolve().parent;T=R/'r10_c16';B=T/'repairs/north-integrated-color-v3';D=T/'repairs/west-color-v1';W=R/'r10_c15/repairs/east-integrated/candidate.png'
EXPECTED='38f9ab047e8dccca8e49e2db392465f42d9447b5edcf4b2aa4d9432ea94304a4'
WEST='e27d76d08c9725bdca0525b45faa8d6ee3f1c2388bfd29e99507559d2450897f'
def arr(p):
 with Image.open(p) as im:return np.asarray(im.convert('RGB')).copy()
def smooth(v,k=17):
 for _ in range(3):
  v=np.stack([np.convolve(np.pad(v[:,c],(k//2,k//2),mode='edge'),np.ones(k)/k,mode='valid') for c in range(3)],axis=1)
 return v
def main():
 assert a.sha(B/'candidate.png')==EXPECTED and a.sha(W)==WEST
 src=arr(B/'candidate.png');west=arr(W);ext=arr(B/'extended-context.png')
 assert hashlib.sha256(west[:,3469:].tobytes()).hexdigest()=='4c9f15367710805deebb860432b93c010911560cd3dccb65687a1f72fd07b5b7'
 # Adjacent 4px averages reduce high-frequency grain without mixing distant materials.
 diff=west[:,-4:].astype(np.float32).mean(axis=1)-src[:,:4].astype(np.float32).mean(axis=1)
 low=np.clip(smooth(diff),-32,32)
 yy=np.arange(4096);fy=np.clip((yy-700)/128,0,1);fy=fy*fy*(3-2*fy)
 fx=np.maximum(0,1-np.arange(230)/229)**2
 field=np.zeros_like(src,dtype=np.int16);field[:,:230]=np.rint(low[:,None,:]*fy[:,None,None]*fx[None,:,None]).astype(np.int16)
 out=np.clip(src.astype(np.int16)+field,0,255).astype(np.uint8)
 actual=out.astype(np.int16)-src.astype(np.int16)
 assert np.array_equal(out[:700],src[:700]) and np.array_equal(out[:,230:],src[:,230:])
 ext2=ext.copy();ext2[115:4211,115:4211]=out
 halo=np.ones((4326,4326),bool);halo[115:4211,115:4211]=False;assert np.array_equal(ext2[halo],ext[halo])
 D.mkdir(parents=True,exist_ok=True);(D/'fields').mkdir(exist_ok=True)
 fp=D/'fields/correction.npz';np.savez_compressed(fp,correction_rgb_i16=actual,raw_edge_difference=diff,low_frequency_difference=low,fade_x=fx,fade_y=fy)
 fi=a.save_image(D/'candidate.png',Image.fromarray(out));ei=a.save_image(D/'extended-context.png',Image.fromarray(ext2))
 mask=(np.max(np.abs(actual),axis=2)>0).astype(np.uint8)*255;mi=a.save_image(D/'fields/changed-pixel-mask.png',Image.fromarray(mask))
 a.QA=D/'qa/assembly';north,ni=a.checked_north();qa=a.write_qa(Image.fromarray(out),Image.fromarray(ext2),north)
 probes(W,D/'candidate.png',D/'qa/external')
 inherited=[];changed=[]
 for q in qa:
  prior=B/'qa/assembly'/Path(q['file']).name
  (inherited if prior.exists() and a.sha(prior)==q['sha256'] else changed).append(q)
 a.save_json(D/'manifest.json',{'createdAtUtc':a.utc_now(),'candidate':fi,'extendedContext':ei,'baseline':{'file':str(B/'candidate.png'),'sha256':EXPECTED},'westReference':{'file':str(W),'sha256':WEST,'east627RawSha256':'4c9f15367710805deebb860432b93c010911560cd3dccb65687a1f72fd07b5b7'},'northReference':ni,'operation':'Add smooth bounded RGB difference field only; no image blur or geometry resampling','authorizedROI':[0,700,230,4096],'maxChannelCorrection':int(np.abs(actual).max()),'channelCap':32,'edgeSamplingWidth':4,'differenceSmoothingKernel':17,'differenceSmoothingPasses':3,'westFadePixels':230,'northFadeRows':[700,828],'allHaloUnchanged':True,'coreAboveY700Unchanged':True,'coreAtOrRightX230Unchanged':True,'field':{'file':str(fp),'sha256':a.sha(fp)},'mask':mi,'qa':qa,'identicalPriorSheets':inherited,'changedSheets':changed,'visualReview':'pending','formalAccepted':False})
 print(json.dumps({'candidate':fi,'extended':ei,'maxChannelCorrection':int(np.abs(actual).max()),'changedSheets':[Path(q['file']).name for q in changed],'inheritedSheets':len(inherited)}))
if __name__=='__main__':main()

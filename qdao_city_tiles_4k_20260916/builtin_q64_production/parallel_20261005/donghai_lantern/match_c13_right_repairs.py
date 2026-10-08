"""Replay the three exact DAY local masks, matching only bounded RGB returns."""
from pathlib import Path
from datetime import datetime,timezone
import sys
sys.dont_write_bytecode=True
import json,numpy as np
from PIL import Image
import sync_c13_right_repairs as s
import finish_west as fw
ROOT=Path(__file__).resolve().parent
DEST=s.DEST/'tone-matched'
def main():
 pair,bs=s.base(1);base=np.asarray(pair).copy();out=base.copy();raw=base.copy();support=np.zeros(base.shape[:2],bool)
 steps=[]
 for i in range(1,4):
  step=s.DEST/f'step{i:02}';plan=s.read(step/'plan.json');r=s.read(step/'native.png.generation.json');s.check(step/'native.png',r['sha256'])
  for key in ('dayManifest','dayGeneratedEdit','dayRecord','dayInputRecord','combinedMask'):s.check(plan[key]['file'],plan[key]['sha256'])
  for ref in r['references']:s.check(ref['file'],ref['sha256'])
  x0,y0,x1,y1=plan['pairRepairRectXYXY'];cx,cy,_,_=plan['pairCropRectXYXY'];h,w=y1-y0,x1-x0
  new=np.asarray(s.img(step/'native.png'))[y0-cy:y1-cy,x0-cx:x1-cx].copy();old=out[y0:y1,x0:x1].copy()
  alpha=np.asarray(Image.open(plan['combinedMask']['file'])).copy();assert alpha.shape==(h,w)
  xx,yy=np.meshgrid(np.arange(w),np.arange(h));distance=np.minimum.reduce([xx,w-1-xx,yy,h-1-yy]).astype(np.float32)
  edge_weight=fw.weight(np.maximum(0,distance-24),128)
  field=np.clip(fw.difference_field(new,old),-24,24)*edge_weight[...,None]
  adjusted=np.rint(np.clip(new.astype(np.float32)+field,0,255)).astype(np.uint8)
  delta=adjusted.astype(np.int16)-new.astype(np.int16);assert np.abs(delta).max()<=24
  raw[y0:y1,x0:x1]=s.blend(raw[y0:y1,x0:x1],new,alpha)
  out[y0:y1,x0:x1]=s.blend(old,adjusted,alpha)
  support[y0:y1,x0:x1]|=alpha>0
  fp=DEST/'fields'/f'step{i:02}.npz';fp.parent.mkdir(parents=True,exist_ok=True)
  np.savez_compressed(fp,source_delta_rgb=delta.astype(np.int8),alpha_u8=alpha,pair_rect_xyxy=np.array([x0,y0,x1,y1]))
  steps.append({'step':i,'plan':s.info(step/'plan.json'),'native':s.info(step/'native.png'),'record':s.info(step/'native.png.generation.json'),'field':s.info(fp),'pairRectXYXY':[x0,y0,x1,y1],'maximumSourceChannelDelta':int(np.abs(delta).max()),'exactDayMask':plan['combinedMask']})
 original=np.asarray(s.img(s.DEST/'step03/output/r08_c13.png'));assert np.array_equal(raw[:,4096:],original),'Unmatched exact-mask replay differs'
 final_delta=np.clip(out[:,4096:].astype(np.int16)-original.astype(np.int16),-24,24).astype(np.int8)
 out[:,4096:]=(original.astype(np.int16)+final_delta.astype(np.int16)).astype(np.uint8)
 assert np.array_equal(out[~support],base[~support]) and np.array_equal(out[:,:4096],base[:,:4096])
 fp=DEST/'fields/final-delta.npz';np.savez_compressed(fp,delta_rgb=final_delta,support=support[:,4096:])
 assert np.array_equal(original.astype(np.int16)+final_delta.astype(np.int16),out[:,4096:])
 meta={'derivedFrom':bs+[s.info(s.DEST/'step03/output/r08_c13.png')],'steps':steps,'colorCorrection':True,'colorCorrectionField':s.info(fp),'maximumFinalChannelDelta':int(np.abs(final_delta).max()),'noResampling':True,'noGeometryFlow':True,'artBlur':False,'dayMasksIdentical':True,'outsideAuthorizedUnionExactlyIdentical':True,'formalAccepted':False}
 output=s.save(DEST/'output/r08_c13.png',Image.fromarray(out[:,4096:]),meta)
 qa=[]
 for i in range(1,4):
  plan=s.read(s.DEST/f'step{i:02}/plan.json');box=plan['pairCropRectXYXY']
  qa.append(s.save(DEST/'qa'/f'local-{i}-full-return.png',Image.fromarray(out).crop(box),{'derivedFrom':[output,s.info(s.WEST)],'pairRectXYXY':box,'pixelScale':1,'visualReview':'pending'}))
 # The common-edge pixels do not change; this provides a direct pending-issue reference.
 qa.append(s.save(DEST/'qa/remaining-common-paving.png',Image.fromarray(out).crop((3889,2148,4284,2448)),{'derivedFrom':[output,s.info(s.WEST)],'pairRectXYXY':[3889,2148,4284,2448],'pixelScale':1,'visualReview':'pending inherited shared-source geometry'}))
 manifest={**meta,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'script':s.info(__file__),'output':output,'c12Unchanged':s.info(s.WEST),'qa':qa,'parameters':{'correctionRadius':128,'fullWeightEdgeBand':24,'maximumSourceChannelDelta':24,'maximumFinalChannelDelta':24,'differenceFieldSmoothing':'three box passes radius12, difference field only','geometryMask':'exact DAY alpha unchanged'},'rawReplayExact':True,'outsideUnionChangedPixels':0,'c13InternalRepairOutsideUnionPreserved':True,'globalStateModified':False,'visualReview':'pending'}
 s.write(DEST/'output/integration-manifest.json',manifest)
 print(json.dumps({'output':output,'c12Unchanged':s.info(s.WEST),'manifest':str(DEST/'output/integration-manifest.json'),'maxDelta':int(np.abs(final_delta).max())},indent=2))
if __name__=='__main__':main()

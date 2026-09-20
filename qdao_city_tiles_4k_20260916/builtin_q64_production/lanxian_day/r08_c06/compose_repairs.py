from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, importlib.util, argparse
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
REPAIR=ROOT/'repairs/v2'; OUT=ROOT/'output'; QA=ROOT/'qa'
VARIANT=ROOT.parent.name
BASE=OUT/f'{VARIANT}_r08_c06_q64_4k_candidate.png'
DEST=OUT/f'{VARIANT}_r08_c06_q64_4k_candidate_v2.png'
EXT=OUT/'extended-context-v2.png'
REPORT=OUT/'repair-v2-assembly.json'
HELPER=Path(r'E:/work/image/tianyong_festival_hd_20260910/seam_helpers.py')
BAND=64
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rgb(p): return np.asarray(Image.open(p).convert('RGB')).copy()
def save(a,p): Image.fromarray(a).save(p,optimize=True)
def inputs():
 plan=read(REPAIR/'plan.json')
 assert sha(BASE)==plan['baseSha256']==read(OUT/'assembly.json')['output']['sha256']
 sources=[]
 for id,box in plan['patches'].items():
  rec=read(REPAIR/'native'/f'{id}.record.json')
  native=REPAIR/'native'/f'{id}.png'
  assert rec['actualNativePixels']==[1254,1254]
  for p,k in [(native,'outputSha256'),(REPAIR/'prompts'/f'{id}.prompt.txt','promptSha256'),(REPAIR/'guides'/f'{id}.layout-only.png','guideSha256')]:
   assert sha(p)==rec[k]
  assert sha(rec['sourceOutputPath'])==sha(native)==rec['sourceOutputSha256']
  assert not rec['backendModelVerified'] and not rec['finalArtUpscaled'] and not rec['resizedAfterGeneration']
  assert rgb(native).shape==(1254,1254,3)
  sources.append({'id':id,'rect':box,'native':str(native),'sha256':sha(native),'record':str(REPAIR/'native'/f'{id}.record.json'),'recordSha256':sha(REPAIR/'native'/f'{id}.record.json'),'sourceOutputPath':rec['sourceOutputPath'],'sourceOutputSha256':rec['sourceOutputSha256']})
 return plan,sources
def check():
 plan,sources=inputs();r=read(REPORT)
 assert r['sources']==sources
 for p,k in [(DEST,r['output']['sha256']),(EXT,r['extendedContext']['sha256']),(Path(__file__),r['scriptSha256']),(HELPER,r['helperSha256'])]: assert sha(p)==k
 a=rgb(DEST); b=rgb(BASE); e=rgb(EXT)
 assert a.shape==(4096,4096,3) and e.shape==(4326,4326,3)
 assert np.array_equal(e[115:4211,115:4211],a)
 outside=np.ones((4096,4096),bool)
 for s in sources:
  x,y,x1,y1=s['rect'];outside[y:y1,x:x1]=False
 assert np.array_equal(a[outside],b[outside])
 for q in r['qa']:assert sha(q['file'])==q['sha256']
 return {'passed':True,'candidate':str(DEST),'sha256':sha(DEST),'size':[4096,4096],'baseNativeCount':16,'repairNativeCount':len(sources),'outsideRepairUnchanged':True,'external4kSeamsAccepted':False}
def main():
 if '--check' in __import__('sys').argv:print(json.dumps(check()));return
 if DEST.exists():raise ValueError('Do not overwrite historical v2; use --check')
 plan,sources=inputs()
 spec=importlib.util.spec_from_file_location('seam_helpers',HELPER);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 minimum=mod._minimum_vertical_seam
 a=rgb(BASE);qa=[];summary=[]
 for s in sources:
  x,y,x1,y1=s['rect']; old=a[y:y1,x:x1].copy();new=rgb(s['native'])
  h,w=old.shape[:2]; xx=np.arange(w)[None,:];yy=np.arange(h)[:,None]
  left=minimum(old[:,:BAND],new[:,:BAND]); right=minimum(old[:,-BAND:],new[:,-BAND:])+w-BAND
  top=minimum(old[:BAND].transpose(1,0,2),new[:BAND].transpose(1,0,2));bottom=minimum(old[-BAND:].transpose(1,0,2),new[-BAND:].transpose(1,0,2))+h-BAND
  mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:])
  merged=np.where(mask[...,None],new,old)
  assert np.all(np.all(merged==new,axis=2)|np.all(merged==old,axis=2))
  a[y:y1,x:x1]=merged
  summary.append({'id':s['id'],'selectedNativePixels':int(mask.sum()),'band':BAND})
 save(a,DEST)
 e=rgb(OUT/'extended-context.png');e[115:4211,115:4211]=a;save(e,EXT)
 over=QA/'v2_overview_1024.png';Image.fromarray(a).resize((1024,1024),Image.Resampling.LANCZOS).save(over,optimize=True);qa.append({'file':str(over),'sha256':sha(over),'kind':'preview_only'})
 for s in sources:
  x,y,x1,y1=s['rect']
  for name,box in [('context',[max(0,x-64),max(0,y-64),min(4096,x1+64),min(4096,y1+64)]),('center',[x+177,y+177,x+1077,y+1077])]:
   l,t,r,b=box;p=QA/f"v2_{s['id']}_{name}_100pct.png";save(a[t:b,l:r],p);qa.append({'file':str(p),'sha256':sha(p),'kind':'native_crop','rect':box,'size':[r-l,b-t],'resized':False})
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_repaired_pending_visual_review_not_published','published':False,'base':{'file':str(BASE),'sha256':sha(BASE)},'sources':sources,'scriptSha256':sha(Path(__file__)),'helperSha256':sha(HELPER),'output':{'file':str(DEST),'sha256':sha(DEST),'size':[4096,4096]},'extendedContext':{'file':str(EXT),'sha256':sha(EXT),'size':[4326,4326]},'method':'four-edge minimum-error hard seam; no resampling, blur, sharpen, color correction, or generated art drawing','finalArtUpscaled':False,'nativeSamplesOnly':True,'outsideRepairUnchanged':True,'external4kSeamsAccepted':False,'nearestCameraAccepted':False,'wholeCityAccepted':False,'composition':summary,'qa':qa,'visualQA':{'status':'pending'}}
 REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(check()))
if __name__=='__main__':main()


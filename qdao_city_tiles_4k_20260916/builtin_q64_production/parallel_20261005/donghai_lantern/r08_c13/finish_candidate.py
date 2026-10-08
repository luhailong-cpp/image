"""Apply final scoped native repairs to the latest coherent festival pair."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
C13=ROOT/'r08_c13'
DEST=C13/'completed-candidate'
BASE12=C13/'west-final/output/r08_c12.png'
BASE13=C13/'right-stone-sync/tone-matched/output/r08_c13.png'
SHA12='c24b061459e3dc89d45fc101c8ddd9d8606433a35ff8fcc29565bf3cce15ddf6'
SHA13='9f88ba04a1f50ca198bd368060d2cba6f83a29bb3f75e2df702504fb8190732f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
def save(p,a,record):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(a).save(p);r={**ref(p),'width':a.shape[1],'height':a.shape[0],**record};write(str(p)+'.generation.json',r);return r
def main():
 assert sha(BASE12)==SHA12 and sha(BASE13)==SHA13
 b12=np.asarray(Image.open(BASE12).convert('RGB'));b13=np.asarray(Image.open(BASE13).convert('RGB'))
 base=np.concatenate((b12,b13),axis=1); result=base.copy(); support=np.zeros(base.shape[:2],bool);records=[];qa=[]
 wall=C13/'repairs/internal-lighting/native/wall.png';wall_rec=read(str(wall)+'.generation.json')
 assert sha(wall)==wall_rec['sha256']
 target=C13/'repairs/internal-lighting/guides/wall-target.png'
 assert np.array_equal(np.asarray(Image.open(target).convert('RGB')),b13[500:1754,2300:3554]),'Old wall target must match latest base within full native window'
 jobs=[{'name':'wall','native':ref(wall),'nativePairXY':[6396,500],'roiPairXYXY':[6756,995,7356,1310],'featherPixels':48,'type':'lighting-only','generationRecord':str(wall)+'.generation.json'}]
 if len(sys.argv)>1:
  paving=read(sys.argv[1]);jobs.append(paving)
 for job in jobs:
  path=Path(job['native']['file']);assert sha(path)==job['native']['sha256'];native=np.asarray(Image.open(path).convert('RGB'));assert native.shape==(1254,1254,3)
  x,y=job['nativePairXY']; l,t,r,b=job['roiPairXYXY']; yy,xx=np.mgrid[:1254,:1254]
  d=np.minimum.reduce((xx+x-l,yy+y-t,r-1-xx-x,b-1-yy-y)).astype(np.float32)
  a=np.clip(d/job['featherPixels'],0,1);a=a*a*(3-2*a);alpha=np.rint(a*255).astype(np.uint8)
  local=result[y:y+1254,x:x+1254];assert local.shape==native.shape
  s=alpha>0;assert not support[y:y+1254,x:x+1254][s].any(),'Repairs must not overlap'
  local[:]=((local.astype(np.uint32)*(255-alpha[:,:,None])+native.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
  support[y:y+1254,x:x+1254]|=s
  mr=save(DEST/'masks'/f"{job['name']}.png",alpha,{'operation':'48-pixel smoothstep bounded return mask','boundsPairXYXY':job['roiPairXYXY'],'nativePairXY':job['nativePairXY']})
  records.append({**job,'mask':mr,'nativeResampled':False,'colorMatched':False})
 assert np.array_equal(result[~support],base[~support])
 common={'derivedFrom':[ref(BASE12),ref(BASE13)],'repairs':records,'artResampled':False,'artUpscaled':False,'blurred':False,'outsideMasksPixelIdentical':True,'completePixelCandidate':True,'formalAccepted':False,'visualReview':'pending','generatedAt':datetime.now(timezone.utc).isoformat()}
 out=DEST/'output';pair=save(out/'pair-r08_c12-c13.png',result,{**common,'operation':'Native patch insertion with bounded local returns','globalRectXYWH':[45056,28672,8192,4096]})
 c12=save(out/'r08_c12.png',result[:,:4096],{**common,'operation':'Exact native left crop of coherent pair','derivedFrom':[pair],'globalRectXYWH':[45056,28672,4096,4096]})
 c13=save(out/'r08_c13.png',result[:,4096:],{**common,'operation':'Exact native right crop of coherent pair','derivedFrom':[pair],'globalRectXYWH':[49152,28672,4096,4096]})
 for j in jobs:
  x,y=j['nativePairXY'];l,t,r,b=j['roiPairXYXY'];name=j['name']; boxes={'complete-return':[x,y,x+1254,y+1254],'top-return':[l-96,t-96,r+96,t+96],'bottom-return':[l-96,b-96,r+96,b+96],'left-return':[l-96,t-96,l+96,b+96],'right-return':[r-96,t-96,r+96,b+96]}
  for suffix,box in boxes.items():
   l1,t1,r1,b1=box;qa.append(save(DEST/'qa'/f'{name}-{suffix}.png',result[t1:b1,l1:r1],{'operation':'Exact native crop of final repair return','derivedFrom':[pair],'sourceCropPairXYXY':box,'resized':False,'finalArt':False}))
 manifest={**common,'pair':pair,'tiles':[c12,c13],'qa':qa,'changedPixels':int(np.any(result!=base,axis=2).sum()),'allRepairsPresent':len(jobs)==2,'script':ref(__file__)}
 write(out/'integration-manifest.json',manifest)
 print(json.dumps({'tiles':[ref(out/'r08_c12.png'),ref(out/'r08_c13.png')],'repairs':len(jobs),'outsideMasksPixelIdentical':True,'changedPixels':manifest['changedPixels']},indent=2))
if __name__=='__main__':main()

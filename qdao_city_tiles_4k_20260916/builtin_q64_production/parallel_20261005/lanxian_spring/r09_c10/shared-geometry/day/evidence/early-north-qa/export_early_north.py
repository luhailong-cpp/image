from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent;TILE=OUT.parent;NORTH=TILE.parent/'r08_c10/selected/core4096.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def save(name,a):
 p=OUT/name
 if p.exists():raise FileExistsError('Existing QA artifact must not be overwritten: '+str(p))
 Image.fromarray(a).save(p);d=ref(p);d['pixels']=[a.shape[1],a.shape[0]];return d
def main():
 assert sha(NORTH)=='bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f'
 north=np.array(Image.open(NORTH).convert('RGB'));top=np.empty((1024,4096,3),np.uint8);sources=[]
 for col in range(1,5):
  p=TILE/'native'/f'r01_c{col:02d}.png';gp=Path(str(p)+'.generation.json');g=json.loads(gp.read_text(encoding='utf-8'));assert sha(p)==g['sha256'];im=Image.open(p);assert im.size==(1254,1254);a=np.array(im.convert('RGB'));top[:,(col-1)*1024:col*1024]=a[115:1139,115:1139];sources.append({**ref(p),'generation':ref(gp),'nativeCoreBoxLTRB':[115,115,1139,1139],'outputCoreBoxLTRB':[(col-1)*1024,0,col*1024,1024]})
 topinfo=save('top-row4096x1024.png',top);checks=[]
 for col in range(1,5):
  x0=(col-1)*1024;x1=col*1024;board=np.concatenate([north[-256:,x0:x1],top[:256,x0:x1]],axis=0);info=save(f'northjoin-c{col:02d}.png',board);info.update(kind='external_north_join',rangeId=f'northjoin-c{col:02d}',targetCoreBoxLTRB=[x0,0,x1,256],northCoreBoxLTRB=[x0,3840,x1,4096],boardJoinY=256,layout='c10 final bottom256 above; r09 actual top256 below',scale=1,resampling='none',actuallyViewed=False);checks.append(info)
  info=save(f'guide-y115-c{col:02d}.png',top[51:179,x0:x1]);info.update(kind='top_reference_band_end',rangeId=f'guide-y115-c{col:02d}',targetCoreBoxLTRB=[x0,51,x1,179],guideBoundaryCoreY=115,boardGuideY=64,scale=1,resampling='none',actuallyViewed=False);checks.append(info)
 for name,box in [('corner-nw',[0,0,512,512]),('corner-ne',[3584,0,4096,512])]:
  x0,y0,x1,y1=box;info=save(name+'.png',top[y0:y1,x0:x1]);info.update(kind='own_upper_corner',rangeId=name,targetCoreBoxLTRB=box,scale=1,resampling='none',actuallyViewed=False);checks.append(info)
 m={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r09_c10','scope':'Early north QA from completed first row only; this is not a4096x4096 whole-tile candidate','sourceNorth':ref(NORTH),'sourceNative':sources,'topRow':topinfo,'topRowPixels':[4096,1024],'construction':'Exact integer core crop[115,115,1139,1139] from each native1254 image; four cores pasted at x0,1024,2048,3072; no scaling/blending/registration','topRowRawRGBSha256':hashlib.sha256(top.tobytes()).hexdigest(),'checks':checks,'inheritanceCondition':'Future final core first1024 rows must be byte-identical to this top row, and north source c10 selected hash must remain unchanged. Any actual changed support intersecting inspected ranges requires changed-region review.','formalAccepted':False,'qualifiedComplete4KCandidate':False,'sourceUnchangedVerified':all(sha(s['file'])==s['sha256'] for s in sources) and sha(NORTH)=='bff348371e3ba8d23fe152885919a94b550807cbccdd1a0dccd2c81abc9f807f'}
 p=OUT/'export.manifest.json'
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'topRow':topinfo,'rangeCount':len(checks),'manifest':str(p)}))
if __name__=='__main__':main()

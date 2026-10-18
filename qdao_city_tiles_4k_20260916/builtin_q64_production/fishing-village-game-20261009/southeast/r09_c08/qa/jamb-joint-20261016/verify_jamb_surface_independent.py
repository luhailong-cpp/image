from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent;Z=Q.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pix(p):return np.array(Image.open(p).convert('RGB'))
proof=read(Q/'jamb-v1-surface-proof.json');inp=read(Q/'jamb-input-v1.json')
raw=pix(proof['raw']);base=pix(proof['input']);assert raw.shape==base.shape==(1254,1254,3)
assert sha(proof['raw'])==proof['rawSha256'] and sha(proof['input'])==proof['inputSha256'] and sha(proof['binaryMask'])==proof['binaryMaskSha256']
maskraw=np.array(Image.open(proof['binaryMask']));assert set(np.unique(maskraw))=={0,255};mask=maskraw==255
old_window_mask=np.array(Image.open(Q.parent/'window-joint-20261016/window-joint-v1-binary-mask.png'))>0
assert not np.any(mask&old_window_mask)
joint=base.copy();joint[mask]=raw[mask];assert np.array_equal(joint,pix(proof['jointCandidate']))
fx,fy,_,_=proof['frameGlobalBox'];records=[];internal=[]
for item in proof['patches']:
 tile,pid=item['tile'],item['patch'];T=Z/tile;sel=read(T/'selected-patches.json');source=T/sel['patches'][pid]
 assert source.resolve()==Path(item['source']).resolve() and sha(source)==item['sourceSha256'];candidate=Path(item['candidate']);assert sha(candidate)==item['candidateSha256']
 a,b=pix(source),pix(candidate);assert a.shape==b.shape==(1254,1254,3)
 ox=(int(tile[5:7])-1)*4096+(int(pid[2])-1)*1024-115;oy=(int(tile[1:3])-1)*4096+(int(pid[1])-1)*1024-115
 yy,xx=np.indices((1254,1254));qx,qy=xx+ox-fx,yy+oy-fy;valid=(xx>=115)&(xx<1139)&(yy>=115)&(yy<1139)&(qx>=0)&(qx<1254)&(qy>=0)&(qy<1254)
 pm=np.zeros((1254,1254),bool);pm[valid]=mask[qy[valid],qx[valid]];assert np.array_equal(a[~pm],b[~pm]);assert np.array_equal(b[pm],raw[qy[pm],qx[pm]])
 halo=np.ones((1254,1254),bool);halo[115:1139,115:1139]=False;assert np.array_equal(a[halo],b[halo])
 wm=np.zeros((1254,1254),bool);wm[valid]=old_window_mask[qy[valid],qx[valid]];assert np.array_equal(a[wm],b[wm])
 records.append(dict(item,independentReplay=True,windowPixelsUnchanged=True,sourceStillCanonical=True))
 # Compare just the old internal evidence regions from exact core coordinates.
 reuse=read(T/'processed/window-joint-20261016-v1/internal-QA-pixel-reuse.json');assert len(reuse['evidence'])==33
 for e in reuse['evidence']:
  assert sha(e['file'])==e['sha256'];x0,y0,x1,y1=e['tileBox'];replay=np.empty((y1-y0,x1-x0,3),np.uint8);coverage=np.zeros((y1-y0,x1-x0),np.uint8)
  for p,rel in sel['patches'].items():
   cx,cy=(int(p[2])-1)*1024,(int(p[1])-1)*1024;ix0,iy0,ix1,iy1=max(x0,cx),max(y0,cy),min(x1,cx+1024),min(y1,cy+1024)
   if ix0>=ix1 or iy0>=iy1:continue
   pa=pix(candidate if p==pid else T/rel);replay[iy0-y0:iy1-y0,ix0-x0:ix1-x0]=pa[115+iy0-cy:115+iy1-cy,115+ix0-cx:115+ix1-cx];coverage[iy0-y0:iy1-y0,ix0-x0:ix1-x0]+=1
  assert np.all(coverage==1) and np.array_equal(replay,pix(e['file']))
  internal.append({'tile':tile,'file':e['file'],'sha256':e['sha256'],'samePixelsWithCurrentPlusCandidateCores':True,'priorStatusPreserved':True})
for e in proof['evidence']:
 assert sha(e['file'])==e['sha256'];x0,y0,x1,y1=e['frameBox'];assert np.array_equal(pix(e['file']),joint[y0:y1,x0:x1])
r={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'independent_same_coordinate_replay_passed','proofFile':str(Q/'jamb-v1-surface-proof.json'),'proofSha256':sha(Q/'jamb-v1-surface-proof.json'),'patches':records,'protectedPriorWindowMaskNonoverlap':True,'windowPixelExactUnchanged':True,'allMaskExteriorAndHalosPixelExactUnchanged':True,'nativeRawPixelsMatchInsideMask':True,'sevenNativeQACropsExact':True,'internalEvidenceUnchangedCount':66,'internalEvidence':internal,'canonicalModified':False,'formalAccepted':False}
out=Q/'jamb-v1-surface-independent-replay.json'
with out.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2)
print(json.dumps({'file':str(out),'status':r['status'],'unchangedInternalEvidence':66,'canonicalModified':False}))

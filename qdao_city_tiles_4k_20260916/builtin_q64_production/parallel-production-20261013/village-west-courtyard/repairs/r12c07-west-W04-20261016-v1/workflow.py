from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,sys
from datetime import datetime,timezone
R=Path(__file__).parent;B=R.parent.parent;Q=B/'qa/r12c07-west-W04-20261016-v1';Q.mkdir(parents=True,exist_ok=True)
E=B/'qa/r12c07-resume2-r19-v1/context-native.png';W=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def dp(cost):
 h,w=cost.shape;prev=np.zeros((h,w),np.int8);v=cost[:,0].copy()
 for x in range(1,w):
  opts=np.stack([np.r_[np.inf,v[:-1]]+.25,v,np.r_[v[1:],np.inf]+.25]);k=opts.argmin(axis=0);prev[:,x]=k-1;v=cost[:,x]+opts[k,np.arange(h)]
 path=np.empty(w,np.int32);y=int(v.argmin())
 for x in range(w-1,-1,-1):
  path[x]=y
  if x:y+=int(prev[y,x])
 return path
mode=sys.argv[1]
if mode=='prepare':
 e=np.asarray(Image.open(E).convert('RGB'));w=np.asarray(Image.open(W).convert('RGB'));assert sha(W)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef';assert e.shape==w.shape==(4326,4326,3)
 edit=np.concatenate([w[3072:4326,3840:4326],e[3072:4326,230:998]],axis=1);actual=np.concatenate([w[3072:4326,3840:4211],e[3072:4326,115:998]],axis=1)
 assert edit.shape==actual.shape==(1254,1254,3);p=R/'W04-v01.input-with-native-donor.png';a=R/'W04-v01.actual-core-input.png';d=R/'west-same-global-donor-230x1254.png';assert not p.exists();Image.fromarray(edit).save(p);Image.fromarray(actual).save(a);Image.fromarray(w[3072:4326,4096:4326]).save(d)
 j={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'name':'W04-v01','base':rec(E),'baseAssembly':rec(E.parent/'assembly.json'),'westAnchor':rec(W),'donor':rec(d),'editInput':rec(p),'actualCoreReference':rec(a),'nativeSize':[1254,1254],'patchContextBox':[-256,3072,998,4326],'globalNativeBox':[24205,48013,25459,49267],'actualCoreBoundaryLocalX':371,'immutableWestAndDonorLocalX':[0,486],'westCoreInputBox':[3840,3072,4211,4326],'westCorePlusHaloInputBox':[3840,3072,4326,4326],'eastR19AfterDonorBox':[230,3072,998,4326],'allowedContextBox':[0,3072,998,4326],'route':'built-in image_gen','actualModel':'not returned','audit':rec(B/'qa/r12c07-west-pair-20261016-v1/old-r05-input-audit-v1.json'),'prompt':(R/'W04-v01.prompt.txt').read_text(encoding='utf-8')};save(R/'W04-v01.request.json',j);print(json.dumps(j,ensure_ascii=False))
elif mode=='archive':
 src=Path(sys.argv[2]);p=R/'W04-v01.native.png';assert not p.exists();shutil.copyfile(src,p);assert Image.open(p).size==(1254,1254);save(R/'W04-v01.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'request':rec(R/'W04-v01.request.json'),'toolOriginal':rec(src),'archivedOriginal':rec(p),'nativeSize':[1254,1254],'route':'built-in image_gen','actualModel':'not returned','noResize':True});print(json.dumps(rec(p)))
elif mode=='compose':
 version=sys.argv[2];outdir=Q/version;assert not outdir.exists();outdir.mkdir();req=json.loads((R/'W04-v01.request.json').read_text(encoding='utf-8'));assert sha(E)==req['base']['sha256'];assert sha(W)==req['westAnchor']['sha256'];e=np.asarray(Image.open(E).convert('RGB'));w=np.asarray(Image.open(W).convert('RGB'));native=np.asarray(Image.open(R/'W04-v01.native.png').convert('RGB'));donor=np.asarray(Image.open(R/'west-same-global-donor-230x1254.png').convert('RGB'));local=native[:,256:1254].copy()
 # Joint source decision: donor/AI path first, then ONE shared outer path.
 # There is no late anchor paste that can cut off an AI transition endpoint.
 err=np.mean(np.abs(donor[:,115:230].astype(float)-local[:,115:230].astype(float)),axis=2);inner=dp(err.T)+115;yy,xx=np.indices((1254,998));takeDonor=xx<=inner[:,None];local[:,:230][takeDonor[:,:230]]=donor[takeDonor[:,:230]]
 cost=np.mean(np.abs(local.astype(float)-e[3072:4326,:998].astype(float)),axis=2);top=dp(cost[:115]);bottom=dp(cost[1139:1254])+1139;right=dp(cost[:,768:998].T)+768;outer=(yy>=top[None,:])&(yy<=bottom[None,:])&(xx<=right[:,None]);dm=np.zeros((4326,4326),np.uint8);gm=np.zeros_like(dm);dm[3072:4326,:998]=(outer&takeDonor);gm[3072:4326,:998]=(outer&~takeDonor);assert not np.any(dm&gm)
 out=e.copy();ids=np.zeros((4326,4326),np.uint8);dy,dx=np.nonzero(dm);gy,gx=np.nonzero(gm);out[dy,dx]=donor[dy-3072,dx];out[gy,gx]=native[gy-3072,gx+256];ids[dy,dx]=1;ids[gy,gx]=2
 for fn,a in [('donor-mask-uint8.npy',dm),('generation-mask-uint8.npy',gm),('source-layer-ids-uint8.npy',ids)]:np.save(outdir/fn,a)
 Image.fromarray(out).save(outdir/'context-native.png');Image.fromarray(out[115:4211,115:4211]).save(outdir/'candidate-native-4096.png');Image.fromarray(ids[3072:4326,:998]*120).save(outdir/'source-layer-local.png')
 replay=e.copy();replay[dy,dx]=donor[dy-3072,dx];replay[gy,gx]=native[gy-3072,gx+256];crops=[]
 boxes={'center':[0,3072,998,4326],'top':[0,2982,1090,3277],'bottom':[0,4096,1090,4326],'left':[0,3072,340,4326],'right':[678,3072,1090,4326]}
 for name,box in boxes.items():
  x0,y0,x1,y1=box;p=outdir/f'{name}-native.png';Image.fromarray(out[y0:y1,x0:x1]).save(p);crops.append({'label':name,**rec(p),'contextBox':box,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=out[y0:y1,x0:x1],axis=2).sum())})
 actual=np.concatenate([w[3187:4211,3866:4211],out[3187:4211,115:805]],axis=1);p=outdir/'W04-actual-core-plus-inward-native.png';Image.fromarray(actual).save(p);actualRecord={**rec(p),'size':[1035,1024],'westContextBox':[3866,3187,4211,4211],'eastContextBox':[115,3187,805,4211],'joinLocalX':345,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=actual,axis=2).sum())}
 t={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA','formalAccepted':False,'base':req['base'],'baseAssembly':req['baseAssembly'],'westAnchor':req['westAnchor'],'request':rec(R/'W04-v01.request.json'),'generationReceipt':rec(R/'W04-v01.generation.json'),'donor':req['donor'],'native':rec(R/'W04-v01.native.png'),'donorOriginInContext':[0,3072],'nativeOriginInContext':[-256,3072],'donorMask':rec(outdir/'donor-mask-uint8.npy'),'generationMask':rec(outdir/'generation-mask-uint8.npy'),'sourceIds':rec(outdir/'source-layer-ids-uint8.npy'),'paths':{'innerDonorLastXByLocalY':inner.tolist(),'outerTopFirstLocalYByX':top.tolist(),'outerBottomLastLocalYByX':bottom.tolist(),'outerRightLastXByLocalY':right.tolist()},'method':'Joint binary donor/AI source selection with one outer DP mask. No post-composition anchor paste. Native offsets only.','context':rec(outdir/'context-native.png'),'candidate':rec(outdir/'candidate-native-4096.png'),'proof':{'fullContextReplayDifferentPixels':int(np.any(replay!=np.asarray(Image.open(outdir/'context-native.png')),axis=2).sum()),'overlapPixelsBetweenSourceMasks':int(np.sum(dm&gm)),'changesAboveY3072':int(np.any(out[:3072]!=e[:3072],axis=2).sum()),'changedPixels':int(np.any(out!=e,axis=2).sum()),'actualCoreEdgeToNativeDonorDifferentPixels':int(np.any(out[3187:4211,115:116]!=w[3187:4211,4211:4212],axis=2).sum()),'westAnchorUnchanged':sha(W)==req['westAnchor']['sha256'],'baseUnchanged':sha(E)==req['base']['sha256'],'noResize':True,'noBlend':True,'noBlur':True},'nativeQACrops':crops,'actualCoreQA':actualRecord,'script':rec(Path(__file__))};save(outdir/'assembly.json',t);print(json.dumps({'context':t['context'],'candidate':t['candidate'],'proof':t['proof'],'output':outdir.as_posix()},ensure_ascii=False))

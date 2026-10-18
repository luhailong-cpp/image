from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, shutil, sys
from datetime import datetime, timezone
R=Path(__file__).parent; B=R.parent.parent; Q=B/'qa/r12c07-west-W02-20261016-v1'; Q.mkdir(parents=True,exist_ok=True)
Y0,Y1=1024,2278
E=B/'qa/r12c07-resume2-r19-v1/context-native.png'; W=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
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
 e=np.asarray(Image.open(E).convert('RGB'));w=np.asarray(Image.open(W).convert('RGB'));assert sha(W)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef';assert sha(E)=='99f50735f137c049b46ad315c5ea11873f9a30f25014561dcee25aaaec3e6f72'
 edit=np.concatenate([w[Y0:Y1,3840:4326],e[Y0:Y1,230:998]],axis=1);actual=np.concatenate([w[Y0:Y1,3840:4211],e[Y0:Y1,115:998]],axis=1)
 assert edit.shape==actual.shape==(1254,1254,3)
 p=R/'W02-v01.input-with-native-donor.png';a=R/'W02-v01.actual-core-input.png';d=R/'west-same-global-donor-230x1254.png';assert not p.exists()
 Image.fromarray(edit).save(p);Image.fromarray(actual).save(a);Image.fromarray(w[Y0:Y1,4096:4326]).save(d)
 j={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'name':'W02-v01','base':rec(E),'baseAssembly':rec(E.parent/'assembly.json'),'westAnchor':rec(W),'westAnchorAssembly':rec(W.parent/'assembly.json'),'donor':rec(d),'editInput':rec(p),'actualCoreReference':rec(a),'nativeSize':[1254,1254],'patchContextBox':[-256,Y0,998,Y1],'globalNativeBox':[24205,45965,25459,47219],'actualCoreBoundaryLocalX':371,'immutableWestAndDonorLocalX':[0,486],'westCoreInputBox':[3840,Y0,4211,Y1],'westCorePlusHaloInputBox':[3840,Y0,4326,Y1],'eastR19AfterDonorBox':[230,Y0,998,Y1],'allowedContextBox':[0,Y0,998,Y1],'route':'built-in image_gen','actualModel':'not returned','audit':rec(B/'qa/r12c07-west-pair-20261016-v1/old-r05-input-audit-v1.json'),'prompt':(R/'W02-v01.prompt.txt').read_text(encoding='utf-8')};save(R/'W02-v01.request.json',j);print(json.dumps({k:j[k] for k in ['base','westAnchor','editInput','actualCoreReference','donor']}))
elif mode=='archive':
 attempt=sys.argv[2];src=Path(sys.argv[3]);p=R/f'{attempt}.native.png';assert not p.exists();shutil.copyfile(src,p);assert Image.open(p).size==(1254,1254)
 save(R/f'{attempt}.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'request':rec(R/f'{attempt}.request.json'),'toolOriginal':rec(src),'archivedOriginal':rec(p),'nativeSize':[1254,1254],'route':'built-in image_gen','actualModel':'not returned','noResize':True});print(json.dumps(rec(p)))
elif mode=='compose':
 attempt,version=sys.argv[2:4];outdir=Q/version;assert not outdir.exists();outdir.mkdir();req=json.loads((R/f'{attempt}.request.json').read_text(encoding='utf-8'));assert sha(E)==req['base']['sha256'];assert sha(W)==req['westAnchor']['sha256']
 e=np.asarray(Image.open(E).convert('RGB'));w=np.asarray(Image.open(W).convert('RGB'));native=np.asarray(Image.open(R/f'{attempt}.native.png').convert('RGB'));donor=np.asarray(Image.open(R/'west-same-global-donor-230x1254.png').convert('RGB'));local=native[:,256:1254].copy()
 err=np.mean(np.abs(donor[:,115:230].astype(float)-local[:,115:230].astype(float)),axis=2);inner=dp(err.T)+115;yy,xx=np.indices((1254,998));takeDonor=xx<=inner[:,None];local[:,:230][takeDonor[:,:230]]=donor[takeDonor[:,:230]]
 cost=np.mean(np.abs(local.astype(float)-e[Y0:Y1,:998].astype(float)),axis=2);top=dp(cost[:115]);bottom=dp(cost[1139:1254])+1139;right=dp(cost[:,768:998].T)+768;outer=(yy>=top[None,:])&(yy<=bottom[None,:])&(xx<=right[:,None]);dm=np.zeros((4326,4326),np.uint8);gm=np.zeros_like(dm);dm[Y0:Y1,:998]=(outer&takeDonor);gm[Y0:Y1,:998]=(outer&~takeDonor);gm[1382:1412,230:260]=0;assert not np.any(dm&gm)
 out=e.copy();ids=np.zeros((4326,4326),np.uint8);dy,dx=np.nonzero(dm);gy,gx=np.nonzero(gm);out[dy,dx]=donor[dy-Y0,dx];out[gy,gx]=native[gy-Y0,gx+256];ids[dy,dx]=1;ids[gy,gx]=2
 for fn,a in [('donor-mask-uint8.npy',dm),('generation-mask-uint8.npy',gm),('source-layer-ids-uint8.npy',ids)]:np.save(outdir/fn,a)
 Image.fromarray(out).save(outdir/'context-native.png');Image.fromarray(out[115:4211,115:4211]).save(outdir/'candidate-native-4096.png');Image.fromarray(ids[Y0:Y1,:998]*120).save(outdir/'source-layer-local.png')
 replay=e.copy();replay[dy,dx]=donor[dy-Y0,dx];replay[gy,gx]=native[gy-Y0,gx+256];crops=[]
 boxes={'center':[0,Y0,998,Y1],'top':[0,Y0-90,1090,Y0+205],'bottom':[0,Y1-205,1090,Y1+90],'left':[0,Y0,340,Y1],'right':[678,Y0,1090,Y1]}
 for name,box in boxes.items():
  x0,y0,x1,y1=box;p=outdir/f'{name}-native.png';Image.fromarray(out[y0:y1,x0:x1]).save(p);crops.append({'label':name,**rec(p),'contextBox':box,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=out[y0:y1,x0:x1],axis=2).sum())})
 actual=np.concatenate([w[Y0+115:Y1-115,3866:4211],out[Y0+115:Y1-115,115:805]],axis=1);p=outdir/'W02-actual-core-plus-inward-native.png';Image.fromarray(actual).save(p);actualRecord={**rec(p),'size':[1035,1024],'westContextBox':[3866,Y0+115,4211,Y1-115],'eastContextBox':[115,Y0+115,805,Y1-115],'joinLocalX':345,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=actual,axis=2).sum())}
 for edge,ya,yb in [('top',Y0-90,Y0+205),('bottom',Y1-205,Y1+90)]:
  for kind,a in [('before',e),('after',out)]:
   aa=np.concatenate([w[ya:yb,3866:4211],a[ya:yb,115:460]],axis=1);p=outdir/f'{edge}-junction-{kind}-native.png';Image.fromarray(aa).save(p);crops.append({'label':f'{edge}-junction-{kind}',**rec(p),'westContextBox':[3866,ya,4211,yb],'eastContextBox':[115,ya,460,yb],'joinLocalX':345,'cropIdentityDifferentPixels':0})
 t={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA','formalAccepted':False,'base':req['base'],'baseAssembly':req['baseAssembly'],'westAnchor':req['westAnchor'],'westAnchorAssembly':req['westAnchorAssembly'],'request':rec(R/f'{attempt}.request.json'),'generationReceipt':rec(R/f'{attempt}.generation.json'),'donor':req['donor'],'native':rec(R/f'{attempt}.native.png'),'donorOriginInContext':[0,Y0],'nativeOriginInContext':[-256,Y0],'donorMask':rec(outdir/'donor-mask-uint8.npy'),'generationMask':rec(outdir/'generation-mask-uint8.npy'),'sourceIds':rec(outdir/'source-layer-ids-uint8.npy'),'paths':{'innerDonorLastXByLocalY':inner.tolist(),'outerTopFirstLocalYByX':top.tolist(),'outerBottomLastLocalYByX':bottom.tolist(),'outerRightLastXByLocalY':right.tolist()},'extraPreservedBaseBox':[230,1382,260,1412],'extraPreservedBaseReason':'Remove unsupported newly generated pebble by retaining exact R19 sand pixels.','method':'Joint binary donor/AI source selection with one outer DP mask. No post-composition anchor paste. Native offsets only.','context':rec(outdir/'context-native.png'),'candidate':rec(outdir/'candidate-native-4096.png'),'proof':{'fullContextReplayDifferentPixels':int(np.any(replay!=np.asarray(Image.open(outdir/'context-native.png')),axis=2).sum()),'overlapPixelsBetweenSourceMasks':int(np.sum(dm&gm)),'changesAboveY1024':int(np.any(out[:Y0]!=e[:Y0],axis=2).sum()),'changesBelowY2278':int(np.any(out[Y1:]!=e[Y1:],axis=2).sum()),'changedPixels':int(np.any(out!=e,axis=2).sum()),'actualCoreEdgeToNativeDonorDifferentPixels':int(np.any(out[Y0+115:Y1-115,115:116]!=w[Y0+115:Y1-115,4211:4212],axis=2).sum()),'westAnchorUnchanged':sha(W)==req['westAnchor']['sha256'],'baseUnchanged':sha(E)==req['base']['sha256'],'noResize':True,'noBlend':True,'noBlur':True},'nativeQACrops':crops,'actualCoreQA':actualRecord,'script':rec(Path(__file__))};save(outdir/'assembly.json',t);print(json.dumps({'context':t['context'],'candidate':t['candidate'],'proof':t['proof'],'output':outdir.as_posix()},ensure_ascii=False))

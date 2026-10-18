from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,shutil
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parent;B=R.parent.parent
E=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
O=B.parent.parent/'fishing-village-game-20261009/southwest'
W=O/'qa/pair-r12c05-r13c05-v1-r12_c05-context-native.png'
WH='ce3d6c864dd8e936a25bfa99dc0b06daa9d5e5db9725fd1f265007edaf57876e'
EH='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,j):
 p=Path(p);assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def img(p):return np.asarray(Image.open(p).convert('RGB'))
def verify():
 assert sha(W)==WH,'West snapshot changed; stop coordinate'
 assert sha(E)==EH,'Own base changed; stop coordinate'
 l=read(O/'current-tile-ledger.json');entry=next(x for x in l['tiles'] if x['tile']=='r12_c05')
 assert entry['nativeContext']['sha256']==WH,'Latest owner ledger selected a different context; stop coordinate'
 return entry
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
 entry=verify();e=img(E);w=img(W)
 assert e.shape==w.shape==(4326,4326,3)
 edit=np.concatenate([w[3072:4326,3584:4326],e[3072:4326,230:742]],axis=1)
 actual=np.concatenate([w[3072:4326,3584:4211],e[3072:4326,115:742]],axis=1)
 assert edit.shape==actual.shape==(1254,1254,3)
 paths={}
 for name,data in [('input-with-native-donor',edit),('actual-core-input',actual),('west-same-global-donor',w[3072:4326,4096:4326])]:
  p=R/f'W04-v01.{name}.png';assert not p.exists();Image.fromarray(data).save(p);paths[name]=rec(p)
 prompt='''Use case: precise-object-edit. Repair image 1, an exact 1254 by 1254 native hand-painted top-down Taoist fantasy coastal water crop. Image 2 shows the actual two tile cores before repair; it is diagnostic reference only. Return image 1 at exactly 1254 by 1254, unchanged camera, scale, framing and coordinate locations.
Image 1 columns x0 through x741 are immutable pixels from the western neighbor including its real east halo. Keep those exact pixels and their fine crisp turquoise water cells, thin white foam branches, transparency, sand and tiny details. Repair only the water transition to their right, principally x742 through x1138, so fine western water detail continues naturally into the existing right-side water without a straight vertical texture-size, sharpness or color boundary. Interweave matching small water cells and foam endpoints, gradually meeting the unchanged original far-right water. Do not make the fine western side coarse, and do not blur, smear or enlarge marks.
This is a WATER TEXTURE repair. Keep all established rock, sand and shoreline silhouettes in their existing positions; do not introduce or remove rocks, beaches, islands, structures, plants or objects. Preserve the top 115 pixels and bottom 115 pixels as close to input as possible for native hard-source closure, and preserve the far-right 115 pixels. Keep natural soft daylight, painterly blue-green clear water, intricate white foam and the established Q-style art. No new geometry, no text, UI, labels, borders, grids, watermarks, camera movement or resizing. Opaque RGB.'''
 p=R/'W04-v01.prompt.txt';assert not p.exists();p.write_text(prompt,encoding='utf-8')
 req={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'id':'r12c06-west-W04-v01','base':rec(E),'baseAssembly':rec(E.parent/'assembly.json'),
  'westSnapshot':rec(W),'westSourceTrace':entry['sourceTrace'],'westArtAudit':entry['artAudit'],'ownerLedger':rec(O/'current-tile-ledger.json'),
  'ownerPermanentlyFrozen':False,'snapshotUseBasis':'recorded adjacent native context adopted by current ledger; hash checked before call and composition',
  'allowedContextBox':[0,3072,742,4326],'patchContextBox':[-512,3072,742,4326],'globalNativeBox':[19853,48013,21107,49267],
  'nativeSize':[1254,1254],'coreSize':1024,'halo':115,'actualCoreBoundaryLocalX':627,'fixedWestAndDonorLocalX':[0,742],
  'westInputContextBox':[3584,3072,4326,4326],'ownInputAfterDonorBox':[230,3072,742,4326],
  'editInput':paths['input-with-native-donor'],'actualCoreReference':paths['actual-core-input'],'donor':paths['west-same-global-donor'],
  'references':[{'role':'edit target; western core plus genuine east halo and current own pixels','image':paths['input-with-native-donor']},
    {'role':'actual corejoin diagnostic; do not output','image':paths['actual-core-input']}],
  'route':'existing built-in image_gen','actualModel':None,'prompt':prompt,'promptFile':rec(p),'noPaidApi':True}
 save(R/'W04-v01.request.json',req)
 print(json.dumps({'request':rec(R/'W04-v01.request.json'),'editInput':req['editInput'],'actualCoreReference':req['actualCoreReference']},ensure_ascii=False))
elif mode=='verify':
 verify();print(json.dumps({'westSnapshot':rec(W),'base':rec(E),'verified':True}))
elif mode=='archive':
 src=Path(sys.argv[2]);p=R/'W04-v01.native.png';assert not p.exists();shutil.copyfile(src,p)
 size=list(Image.open(p).size)
 save(R/'W04-v01.generation.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'request':rec(R/'W04-v01.request.json'),
  'toolOriginal':rec(src),'archivedOriginal':rec(p),'nativeSize':size,'route':'existing built-in image_gen','actualModel':None,'noResize':True})
 assert size==[1254,1254],f'Unexpected native size {size}; never resample'
 print(json.dumps(rec(p)))
elif mode=='compose':
 verify();req=read(R/'W04-v01.request.json');outdir=R/'candidate-v1';outdir.mkdir(exist_ok=False)
 e=img(E);w=img(W);native=img(R/'W04-v01.native.png');assert native.shape==(1254,1254,3)
 donor=img(req['donor']['path']);local=native[:,512:1254].copy()
 err=np.mean(np.abs(donor[:,115:230].astype(float)-local[:,115:230].astype(float)),axis=2)
 inner=dp(err.T)+115;yy,xx=np.indices((1254,742));takeDonor=xx<=inner[:,None]
 local[:,:230][takeDonor[:,:230]]=donor[takeDonor[:,:230]]
 cost=np.mean(np.abs(local.astype(float)-e[3072:4326,:742].astype(float)),axis=2)
 top=dp(cost[:115]);bottom=dp(cost[1139:1254])+1139;right=dp(cost[:,512:742].T)+512
 outer=(yy>=top[None,:])&(yy<=bottom[None,:])&(xx<=right[:,None])
 dm=np.zeros((4326,4326),np.uint8);gm=np.zeros_like(dm)
 dm[3072:4326,:742]=outer&takeDonor;gm[3072:4326,:742]=outer&~takeDonor
 assert not np.any(dm&gm)
 out=e.copy();ids=np.zeros((4326,4326),np.uint8);dy,dx=np.nonzero(dm);gy,gx=np.nonzero(gm)
 out[dy,dx]=donor[dy-3072,dx];out[gy,gx]=native[gy-3072,gx+512];ids[dy,dx]=1;ids[gy,gx]=2
 changed=np.any(out!=e,axis=2).astype(np.uint8)
 assert not changed[:3072].any() and not changed[:,742:].any()
 for fn,a in [('donor-mask-uint8.npy',dm),('generation-mask-uint8.npy',gm),('source-layer-ids-uint8.npy',ids),('changed-mask-uint8.npy',changed)]:np.save(outdir/fn,a)
 Image.fromarray(out).save(outdir/'context-native.png');Image.fromarray(out[115:4211,115:4211]).save(outdir/'candidate-native-4096.png')
 Image.fromarray(ids[3072:4326,:742]*120).save(outdir/'source-layer-local.png')
 replay=e.copy();replay[dy,dx]=donor[dy-3072,dx];replay[gy,gx]=native[gy-3072,gx+512]
 crops=[]
 boxes={'center':[0,3072,742,4326],'top':[0,2982,834,3277],'bottom':[0,4096,834,4326],'left':[0,3072,340,4326],'right':[422,3072,834,4326]}
 for name,box in boxes.items():
  x0,y0,x1,y1=box;p=outdir/f'{name}-native.png';Image.fromarray(out[y0:y1,x0:x1]).save(p)
  crops.append({'label':name,**rec(p),'contextBox':box,'cropIdentityDifferentPixels':int(np.any(img(p)!=out[y0:y1,x0:x1],axis=2).sum())})
 actual=np.concatenate([w[3187:4211,3866:4211],out[3187:4211,115:805]],axis=1);p=outdir/'W04-actual-core-plus-inward-native.png';Image.fromarray(actual).save(p)
 actual_rec={**rec(p),'size':[1035,1024],'westContextBox':[3866,3187,4211,4211],'eastContextBox':[115,3187,805,4211],'joinLocalX':345}
 cy,cx=np.nonzero(changed)
 t={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA','formalAccepted':False,'base':req['base'],'baseAssembly':req['baseAssembly'],
  'westSnapshot':req['westSnapshot'],'westSourceTrace':req['westSourceTrace'],'westArtAudit':req['westArtAudit'],'ownerPermanentlyFrozen':False,
  'request':rec(R/'W04-v01.request.json'),'generationReceipt':rec(R/'W04-v01.generation.json'),'donor':req['donor'],'native':rec(R/'W04-v01.native.png'),
  'donorOriginInContext':[0,3072],'nativeOriginInContext':[-512,3072],'donorMask':rec(outdir/'donor-mask-uint8.npy'),'generationMask':rec(outdir/'generation-mask-uint8.npy'),
  'sourceIds':rec(outdir/'source-layer-ids-uint8.npy'),'changedMask':rec(outdir/'changed-mask-uint8.npy'),
  'paths':{'innerDonorLastXByLocalY':inner.tolist(),'outerTopFirstLocalYByX':top.tolist(),'outerBottomLastLocalYByX':bottom.tolist(),'outerRightLastXByLocalY':right.tolist()},
  'method':'Native joint donor/generated source decision under one shared outer hard mask; no late donor paste, blending, blur or resampling.',
  'context':rec(outdir/'context-native.png'),'candidate':rec(outdir/'candidate-native-4096.png'),
  'proof':{'fullContextReplayDifferentPixels':int(np.any(replay!=img(outdir/'context-native.png'),axis=2).sum()),'maskOverlapPixels':int((dm&gm).sum()),
   'changesAboveY3072':int(changed[:3072].sum()),'changesAtOrRightOfX742':int(changed[:,742:].sum()),'changedPixels':int(changed.sum()),
   'changedContextBBox':[int(cx.min()),int(cy.min()),int(cx.max()+1),int(cy.max()+1)] if cx.size else None,
   'actualCoreEdgeToNativeDonorDifferentPixels':int(np.any(out[3187:4211,115:116]!=w[3187:4211,4211:4212],axis=2).sum()),
   'southContextX0To1254ChangedPixels':int(changed[4096:4326,:1254].sum()),'noResize':True,'noBlend':True,'noBlur':True},
  'nativeQACrops':crops,'actualCoreQA':actual_rec,'script':rec(Path(__file__))}
 verify();save(outdir/'assembly.json',t)
 print(json.dumps({'context':t['context'],'candidate':t['candidate'],'proof':t['proof'],'actualCoreQA':actual_rec},ensure_ascii=False))

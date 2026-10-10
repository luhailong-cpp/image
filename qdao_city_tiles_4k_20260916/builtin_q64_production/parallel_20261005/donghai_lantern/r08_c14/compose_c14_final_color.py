from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
import compose_c14_water_repairs as q
T=Path(__file__).resolve().parent;D=T/'water-repaired-v2';q.DEST=D
sha=q.sha;read=q.read;info=q.info;save=q.save_image;write=q.write_json
basep=T/'water-repaired/output/r08_c14.png';assert sha(basep)=='02319f7664c691de68d1f4ccfbb6d9661642653548ff3dc51a66a156f2765d5b'
assert not (D/'output/r08_c14.png').exists(),'Immutable candidate already exists'
base=np.asarray(Image.open(basep).convert('RGB'));result=base.copy();support=np.zeros((4096,4096),bool)
a=read(T/'repairs/wood-color-final/integration.json');b=read(T/'repairs/water-bottom-color-final/completion.json')
ops=[{'id':'wood-color-A','rect':a['cropXYXY'],'roi':a['roiXYXY'],'source':a['native'],'mask':a['mask'],'contract':info(T/'repairs/wood-color-final/integration.json')},{'id':'water-color-B','rect':b['targetTileRectXYXY'],'roi':b['targetTileRectXYXY'],'source':b['patch'],'mask':b['mask'],'contract':info(T/'repairs/water-bottom-color-final/completion.json')}]
for op in ops:
 assert sha(op['source']['file'])==op['source']['sha256'] and sha(op['mask']['file'])==op['mask']['sha256']
 x,y,x1,y1=op['rect'];n=np.asarray(Image.open(op['source']['file']).convert('RGB'));m=np.asarray(Image.open(op['mask']['file']).convert('L'));old=result[y:y1,x:x1].copy();assert old.shape==n.shape and m.shape==n.shape[:2];assert not support[y:y1,x:x1][m>0].any(),'Repair supports intersect'
 result[y:y1,x:x1]=((old.astype(np.uint32)*(255-m[:,:,None])+n.astype(np.uint32)*m[:,:,None]+127)//255).astype(np.uint8);support[y:y1,x:x1]|=m>0
 op['changedPixels']=int(np.any(old!=result[y:y1,x:x1],axis=2).sum())
assert np.array_equal(result[~support],base[~support]);assert np.array_equal(result[:,:627],base[:,:627]);assert np.array_equal(result[:,-627:],base[:,-627:])
common={'operation':'Two independent 48px-return native local paint-continuity repairs','derivedFrom':[info(basep),a['native'],b['native']],'repairOperations':ops,'artResampled':False,'artUpscaled':False,'geometryChanged':False,'completePixelCandidate':True,'formalAccepted':False,'clientAccepted':False,'wholeCityComplete':False,'currentDayPostRepairsAppliedToFestival':True,'priorIntegrationManifest':info(T/'water-repaired/output/tone-assembly-manifest.json'),'outsideRepairMaskPixelIdentical':True,'west627PixelIdentical':True,'east627PixelIdentical':True,'visualReview':'local patches reviewed; combined affected QA pending'}
candidate=save(D/'output/r08_c14.png',result,common)
pm=read(T/'water-repaired/output/tone-assembly-manifest.json');extended=np.array(Image.open(pm['extendedContext']['file']).convert('RGB'));assert sha(pm['extendedContext']['file'])==pm['extendedContext']['sha256'];extended[115:4211,115:4211]=result
ex=save(D/'output/extended-context.png',extended,{**common,'haloSource':pm['extendedContext'],'cropXYXY':[115,115,4211,4211]});preview=save(D/'output/preview-1024.png',Image.fromarray(result).resize((1024,1024),Image.Resampling.LANCZOS),{'derivedFrom':[candidate],'operation':'Preview only','artResampled':True,'finalArt':False})
qa=q.export_qa(result,candidate,read(T/'repairs/water-repair-plan.json'),'all')
for ident,rect,roi in [('A',a['cropXYXY'],a['roiXYXY']),('B',b['windowTileRectXYXY'],b['targetTileRectXYXY'])]:
 l,t,r,bottom=roi
 for name,box in {'full1254':rect,'left':[l-96,t-96,l+96,bottom+96],'right':[r-96,t-96,r+96,bottom+96],'top':[l-96,t-96,r+96,t+96],'bottom':[l-96,bottom-96,r+96,bottom+96]}.items():qa.append(save(D/'qa'/f'local-{ident}-{name}.png',Image.fromarray(result).crop(box),{'derivedFrom':[candidate],'operation':'exact native crop','tileRectXYXY':box,'pixelScale':1}))
comparisons=[]
for entry in qa:
 p=Path(entry['file']);prior=T/'water-repaired/qa'/p.name
 if prior.exists():comparisons.append({'name':p.name,'prior':info(prior),'current':info(p),'pixelIdentical':bool(np.array_equal(np.array(Image.open(prior)),np.array(Image.open(p))))})
proof={'base':info(basep),'candidate':candidate,'repairOperations':ops,'changedPixels':int(np.any(result!=base,axis=2).sum()),'maskNonzeroPixels':int(support.sum()),'outsideMaskChangedPixels':0,'west627PixelIdentical':True,'east627PixelIdentical':True,'allFourExternal128EdgesPixelIdentical':all(np.array_equal(v,w) for v,w in [(result[:128],base[:128]),(result[-128:],base[-128:]),(result[:,:128],base[:,:128]),(result[:,-128:],base[:,-128:])]),'qaComparisons':comparisons}
write(D/'qa/exact-outside-proof.json',proof);write(D/'output/tone-assembly-manifest.json',{**common,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'script':info(__file__),'candidate':candidate,'extendedContext':ex,'preview':preview,'qa':qa,'exactOutsideProof':info(D/'qa/exact-outside-proof.json')})
print(json.dumps({'candidate':candidate,'changedQA':[e['name'] for e in comparisons if not e['pixelIdentical']],'outsideMaskChangedPixels':0},indent=2))
